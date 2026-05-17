import { useRef, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Grid,
  Column,
  Tile,
  SkeletonText,
  SkeletonPlaceholder,
  Search,
  Tag,
  Button,
  Modal,
  TextInput,
  TextArea,
  InlineLoading,
  InlineNotification,
  ToastNotification,
  CodeSnippet,
} from '@carbon/react';
import {
  DocumentBlank,
  Upload,
  CheckmarkFilled,
  Time,
  TrashCan,
  Db2Database,
  Add,
  View,
} from '@carbon/icons-react';
import { knowledgeBaseService } from '../../services/platformService';
import './KnowledgeBase.scss';

const formatBytes = (bytes = 0) => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const KnowledgeBase = () => {
  const queryClient = useQueryClient();
  const fileInputRef = useRef(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searchError, setSearchError] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [isTextIngestOpen, setIsTextIngestOpen] = useState(false);
  const [textForm, setTextForm] = useState({ title: '', content: '', tags: '' });
  const [toast, setToast] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const [viewDocId, setViewDocId] = useState(null);

  const { data: status, isLoading: statusLoading } = useQuery({
    queryKey: ['kb-status'],
    queryFn: knowledgeBaseService.getStatus,
    refetchOnWindowFocus: true,
    refetchInterval: (q) => {
      const st = q.state.data;
      const docs = queryClient.getQueryData(['kb-documents']);
      if (!st || !Array.isArray(docs)) return 6000;
      if (st.document_count !== docs.length) return 1500;
      const sumChunks = docs.reduce((acc, d) => acc + (d.chunk_count || 0), 0);
      if (st.chunk_count !== sumChunks) return 1500;
      return 12000;
    },
  });

  const { data: documents = [], isLoading: docsLoading } = useQuery({
    queryKey: ['kb-documents'],
    queryFn: knowledgeBaseService.listDocuments,
    refetchOnWindowFocus: true,
    refetchInterval: (q) => {
      const st = queryClient.getQueryData(['kb-status']);
      const docs = q.state.data;
      if (!Array.isArray(docs)) return 6000;
      if (!st) return 6000;
      if (st.document_count !== docs.length) return 1500;
      const sumChunks = docs.reduce((acc, d) => acc + (d.chunk_count || 0), 0);
      if (st.chunk_count !== sumChunks) return 1500;
      return 12000;
    },
  });

  const {
    data: docDetail,
    isFetching: detailLoading,
    isError: detailIsError,
    error: detailError,
  } = useQuery({
    queryKey: ['kb-document', viewDocId],
    queryFn: () => knowledgeBaseService.getDocument(viewDocId),
    enabled: Boolean(viewDocId),
  });

  const syncListAfterIngest = async (docId) => {
    for (let i = 0; i < 15; i += 1) {
      await queryClient.refetchQueries({ queryKey: ['kb-documents'] });
      await queryClient.refetchQueries({ queryKey: ['kb-status'] });
      const list = queryClient.getQueryData(['kb-documents']);
      const st = queryClient.getQueryData(['kb-status']);
      if (
        Array.isArray(list) &&
        list.some((d) => d.id === docId) &&
        st &&
        st.document_count === list.length
      ) {
        const sumChunks = list.reduce((acc, d) => acc + (d.chunk_count || 0), 0);
        if (st.chunk_count === sumChunks) {
          return;
        }
      }
      await new Promise((r) => setTimeout(r, 300));
    }
  };

  const uploadFileMutation = useMutation({
    mutationFn: ({ file, title, tags }) =>
      knowledgeBaseService.uploadFile(file, title, tags),
    onSuccess: async (doc) => {
      setToast({ kind: 'success', title: 'Ingested', subtitle: `${doc.title} (${doc.chunk_count} chunks)` });
      queryClient.invalidateQueries({ queryKey: ['kb-documents'] });
      queryClient.invalidateQueries({ queryKey: ['kb-status'] });
      await syncListAfterIngest(doc.id);
      setIsUploadOpen(false);
      setUploadError(null);
    },
    onError: (err) => {
      setUploadError(err?.response?.data?.detail || err.message || 'Upload failed');
    },
  });

  const ingestTextMutation = useMutation({
    mutationFn: (payload) => knowledgeBaseService.ingestText(payload),
    onSuccess: async (doc) => {
      setToast({ kind: 'success', title: 'Ingested', subtitle: `${doc.title} (${doc.chunk_count} chunks)` });
      queryClient.invalidateQueries({ queryKey: ['kb-documents'] });
      queryClient.invalidateQueries({ queryKey: ['kb-status'] });
      await syncListAfterIngest(doc.id);
      setIsTextIngestOpen(false);
      setTextForm({ title: '', content: '', tags: '' });
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'Ingest failed',
        subtitle: err?.response?.data?.detail || err.message,
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => knowledgeBaseService.deleteDocument(id),
    onSuccess: (_, docId) => {
      if (viewDocId === docId) {
        setViewDocId(null);
      }
      setToast({ kind: 'success', title: 'Deleted', subtitle: 'Document removed from knowledge base' });
      queryClient.invalidateQueries({ queryKey: ['kb-documents'] });
      queryClient.invalidateQueries({ queryKey: ['kb-status'] });
      queryClient.removeQueries({ queryKey: ['kb-document', docId] });
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'Delete failed',
        subtitle: err?.response?.data?.detail || err.message,
      });
    },
  });

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    setSearchError(null);
    try {
      const result = await knowledgeBaseService.search(searchQuery.trim(), 4);
      setSearchResults(result.results || []);
    } catch (err) {
      setSearchError(err?.response?.data?.detail || err.message || 'Search failed');
      setSearchResults(null);
    } finally {
      setIsSearching(false);
    }
  };

  const handleFileSelected = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadError(null);
    uploadFileMutation.mutate({ file, title: file.name, tags: '' });
    event.target.value = '';
  };

  if (statusLoading) return <KnowledgeBaseSkeleton />;

  const backendHealthy = !!status?.embeddings_healthy;
  const backendLabel = status?.backend === 'db2' ? 'IBM Db2 Vector' : 'In-memory';
  const vectorDbConcern =
    status?.vector_db_type === 'db2' && status?.vector_db_reachable === false;
  const vectorDbIconColor = vectorDbConcern ? '#da1e28' : '#42be65';

  return (
    <div className="knowledge-base-page">
      <input
        ref={fileInputRef}
        type="file"
        accept=".md,.markdown,.txt,.pdf,.docx,.json,.yaml,.yml,.js,.jsx,.ts,.tsx,.py,.java,.go,.rs,.rb,.c,.cpp,.h,.hpp,.sh,.html,.css,.scss"
        style={{ display: 'none' }}
        onChange={handleFileSelected}
      />

      <div className="page-header">
        <div className="page-header__title">
          <DocumentBlank size={32} />
          <h1>Knowledge Base</h1>
        </div>
        <p className="page-header__description">
          Upload organizational docs and code; agents retrieve relevant context during PR review via Db2 + Ollama embeddings.
        </p>
      </div>

      <Grid className="knowledge-base-grid" narrow>
        <Column lg={4} md={2} sm={2}>
          <Tile className="stat-tile">
            <div className="stat-tile__icon"><DocumentBlank size={24} /></div>
            <div className="stat-tile__content">
              <span className="stat-tile__value">{status?.document_count ?? 0}</span>
              <span className="stat-tile__label">Documents</span>
            </div>
          </Tile>
        </Column>

        <Column lg={4} md={2} sm={2}>
          <Tile className="stat-tile">
            <div className="stat-tile__icon"><CheckmarkFilled size={24} /></div>
            <div className="stat-tile__content">
              <span className="stat-tile__value">{status?.chunk_count ?? 0}</span>
              <span className="stat-tile__label">Indexed Chunks</span>
            </div>
          </Tile>
        </Column>

        <Column lg={4} md={2} sm={2}>
          <Tile className="stat-tile">
            <div className="stat-tile__icon"><Db2Database size={24} style={{ color: vectorDbIconColor }} /></div>
            <div className="stat-tile__content">
              <span className="stat-tile__value">{backendLabel}</span>
              <span className="stat-tile__label">Vector Backend</span>
            </div>
          </Tile>
        </Column>

        <Column lg={4} md={2} sm={2}>
          <Tile className="stat-tile">
            <div className="stat-tile__icon">
              <CheckmarkFilled size={24} style={{ color: backendHealthy ? '#42be65' : '#da1e28' }} />
            </div>
            <div className="stat-tile__content">
              <span className="stat-tile__value">{backendHealthy ? 'Healthy' : 'Unreachable'}</span>
              <span className="stat-tile__label">Embeddings ({status?.embedding_model || 'n/a'})</span>
            </div>
          </Tile>
        </Column>

        {vectorDbConcern && (
          <Column lg={16} md={8} sm={4}>
            <InlineNotification
              kind="error"
              title="Vector database unreachable"
              subtitle={status?.vector_db_error || status?.vector_db_detail || 'Dexter will keep documents in local SQLite + memory only until Db2 accepts connections.'}
              lowContrast
              hideCloseButton
            />
          </Column>
        )}

        {Array.isArray(documents) && status && (
          status.document_count !== documents.length ||
          status.chunk_count !== documents.reduce((acc, d) => acc + (d.chunk_count || 0), 0)
        ) && (
          <Column lg={16} md={8} sm={4}>
            <InlineNotification
              kind="warning"
              title="Syncing knowledge base"
              subtitle="Document or chunk counts don’t match the cached list yet. Refreshing automatically…"
              lowContrast
              hideCloseButton
            />
          </Column>
        )}

        <Column lg={16} md={8} sm={4}>
          <Tile className="search-tile">
            <div className="search-section">
              <Search
                size="lg"
                placeholder="Try: 'how do I handle AWS credentials safely'"
                labelText="Semantic search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') handleSearch(); }}
                className="knowledge-search"
              />
              <Button kind="tertiary" onClick={handleSearch} disabled={isSearching || !searchQuery.trim()}>
                {isSearching ? <InlineLoading description="Searching..." /> : 'Search'}
              </Button>
              <Button kind="ghost" renderIcon={Add} onClick={() => setIsTextIngestOpen(true)}>
                Paste Text
              </Button>
              <Button kind="primary" renderIcon={Upload} onClick={() => fileInputRef.current?.click()} disabled={uploadFileMutation.isPending}>
                {uploadFileMutation.isPending ? 'Uploading...' : 'Upload File'}
              </Button>
            </div>
            {searchError && (
              <InlineNotification kind="error" title="Search failed" subtitle={searchError} hideCloseButton lowContrast />
            )}
            {searchResults && (
              <div className="kb-search-results">
                <h4>{searchResults.length} matching chunk(s)</h4>
                {searchResults.length === 0 && <p>No matches. Ingest more documents.</p>}
                {searchResults.map((r) => (
                  <div key={`${r.document_id}-${r.chunk_index}`} className="kb-search-result">
                    <div className="kb-search-result__header">
                      <Tag type="blue" size="sm">score {r.score}</Tag>
                      <Tag type="cool-gray" size="sm">{r.metadata?.title || r.document_id}</Tag>
                      <Tag type="gray" size="sm">chunk #{r.chunk_index}</Tag>
                    </div>
                    <CodeSnippet type="multi" wrapText hideCopyButton>
                      {r.content}
                    </CodeSnippet>
                  </div>
                ))}
              </div>
            )}
          </Tile>
        </Column>

        <Column lg={16} md={8} sm={4}>
          <Tile className="documents-tile">
            <div className="section-header">
              <h2>Ingested Documents</h2>
              <p className="section-subtitle">
                Stored in {backendLabel}, embedded via {status?.embedding_model}.
              </p>
            </div>
            {docsLoading ? (
              <SkeletonPlaceholder style={{ height: 200 }} />
            ) : documents.length === 0 ? (
              <div className="empty-state">
                <DocumentBlank size={48} />
                <h3>No documents yet</h3>
                <p>Upload a markdown file or paste text to bootstrap the RAG corpus.</p>
              </div>
            ) : (
              <div className="document-grid">
                {documents.map((doc) => (
                  <div key={doc.id} className="document-card">
                    <div className="document-card__header">
                      <div className="document-card__icon"><DocumentBlank size={20} /></div>
                      <Tag type="purple" size="sm">{doc.chunk_count} chunks</Tag>
                    </div>
                    <div className="document-card__body">
                      <h3 className="document-card__title">{doc.title}</h3>
                      <p className="document-card__description">{doc.source}</p>
                      {doc.tags?.length > 0 && (
                        <div className="tag-list">
                          {doc.tags.map((tag) => (
                            <Tag key={tag} type="cool-gray" size="sm">{tag}</Tag>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="document-card__footer">
                      <span className="meta-item">
                        <Time size={16} /> {new Date(doc.created_at).toLocaleString()}
                      </span>
                      <span className="meta-item">{formatBytes(doc.size_bytes)}</span>
                      <div className="document-card__actions">
                        <Button
                          kind="secondary"
                          size="sm"
                          renderIcon={View}
                          onClick={() => setViewDocId(doc.id)}
                        >
                          View
                        </Button>
                        <Button
                          kind="danger--ghost"
                          size="sm"
                          renderIcon={TrashCan}
                          onClick={() => deleteMutation.mutate(doc.id)}
                          disabled={deleteMutation.isPending}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Tile>
        </Column>
      </Grid>

      <Modal
        open={Boolean(viewDocId)}
        onRequestClose={() => setViewDocId(null)}
        modalHeading={docDetail?.title || 'Document'}
        size="lg"
        passiveModal
        aria-label="View knowledge base document"
      >
        {detailLoading && <InlineLoading description="Loading document…" />}
        {detailIsError && (
          <InlineNotification
            kind="error"
            title="Could not load document"
            subtitle={
              detailError?.response?.data?.detail ||
              detailError?.message ||
              'Request failed'
            }
            lowContrast
            hideCloseButton
          />
        )}
        {docDetail && !detailLoading && (
          <div className="document-preview">
            <div className="document-preview__meta">
              <Tag type="purple" size="sm">{docDetail.chunk_count} chunks</Tag>
              <Tag type="cool-gray" size="sm">{docDetail.content_type}</Tag>
              <span className="document-preview__source">{docDetail.source}</span>
            </div>
            {docDetail.tags?.length > 0 && (
              <div className="document-preview__tags">
                <h4>Tags</h4>
                <div className="tag-list">
                  {docDetail.tags.map((tag) => (
                    <Tag key={tag} type="cool-gray" size="sm">{tag}</Tag>
                  ))}
                </div>
              </div>
            )}
            <div className="document-preview__content">
              <h4>Chunks (stored text)</h4>
              <p className="cds--helper-text" style={{ marginBottom: '1rem' }}>
                Embeddings are stored for search/RAG; below is the raw chunk text ingested into the knowledge base.
              </p>
              {(docDetail.chunks || []).map((ch) => (
                <div key={ch.id} className="kb-chunk-block">
                  <div className="kb-chunk-block__header">
                    <Tag type="blue" size="sm">chunk {ch.chunk_index}</Tag>
                    {ch.metadata?.source && (
                      <Tag type="gray" size="sm">{ch.metadata.source}</Tag>
                    )}
                  </div>
                  <CodeSnippet type="multi" wrapText hideCopyButton>
                    {ch.content}
                  </CodeSnippet>
                </div>
              ))}
            </div>
          </div>
        )}
      </Modal>

      <Modal
        open={isTextIngestOpen}
        onRequestClose={() => setIsTextIngestOpen(false)}
        modalHeading="Add document by pasting text"
        primaryButtonText={ingestTextMutation.isPending ? 'Ingesting...' : 'Ingest'}
        secondaryButtonText="Cancel"
        primaryButtonDisabled={ingestTextMutation.isPending || !textForm.title.trim() || !textForm.content.trim()}
        onRequestSubmit={() =>
          ingestTextMutation.mutate({
            title: textForm.title.trim(),
            content: textForm.content,
            tags: textForm.tags.split(',').map((t) => t.trim()).filter(Boolean),
          })
        }
      >
        <p style={{ marginBottom: '1rem' }}>
          Useful for pasting coding standards, ADRs, runbooks, security policies, etc.
        </p>
        <TextInput
          id="kb-title"
          labelText="Title"
          value={textForm.title}
          onChange={(e) => setTextForm((prev) => ({ ...prev, title: e.target.value }))}
        />
        <TextInput
          id="kb-tags"
          labelText="Tags (comma separated)"
          placeholder="security, architecture, ibm"
          value={textForm.tags}
          onChange={(e) => setTextForm((prev) => ({ ...prev, tags: e.target.value }))}
        />
        <TextArea
          id="kb-content"
          labelText="Content"
          rows={10}
          value={textForm.content}
          onChange={(e) => setTextForm((prev) => ({ ...prev, content: e.target.value }))}
        />
      </Modal>

      <Modal
        open={isUploadOpen}
        onRequestClose={() => { setIsUploadOpen(false); setUploadError(null); }}
        modalHeading="Upload document"
        passiveModal
      >
        {uploadError && (
          <InlineNotification kind="error" title="Upload failed" subtitle={uploadError} hideCloseButton lowContrast />
        )}
        <p>Click the button to select a UTF-8 text/markdown/code file.</p>
        <Button kind="primary" renderIcon={Upload} onClick={() => fileInputRef.current?.click()}>
          Choose file
        </Button>
      </Modal>

      {toast && (
        <ToastNotification
          kind={toast.kind}
          title={toast.title}
          subtitle={toast.subtitle}
          timeout={5000}
          onClose={() => setToast(null)}
          style={{ position: 'fixed', bottom: 16, right: 16, zIndex: 9000 }}
        />
      )}
    </div>
  );
};

const KnowledgeBaseSkeleton = () => (
  <div className="knowledge-base-page">
    <div className="page-header">
      <SkeletonText heading width="30%" />
      <SkeletonText width="60%" />
    </div>
    <Grid narrow>
      {[0, 1, 2, 3].map((i) => (
        <Column lg={4} md={2} sm={2} key={i}>
          <Tile><SkeletonPlaceholder style={{ height: 100 }} /></Tile>
        </Column>
      ))}
      <Column lg={16} md={8} sm={4}>
        <Tile><SkeletonPlaceholder style={{ height: 400 }} /></Tile>
      </Column>
    </Grid>
  </div>
);

export default KnowledgeBase;

// Made with Bob
