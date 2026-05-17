import { useLayoutEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Grid,
  Column,
  Button,
  Tile,
  Theme,
  Header,
  HeaderName,
  HeaderNavigation,
  HeaderMenuItem,
  HeaderGlobalBar,
  HeaderGlobalAction,
  SkipToContent,
} from '@carbon/react';
import {
  ArrowRight,
  Security,
  Bot,
  Book,
  LogoGithub,
  ChartLine,
  Settings,
  Asleep,
  Light,
  Flash,
  UserSpeaker,
} from '@carbon/icons-react';
import { GroupedBarChart } from '@carbon/charts-react';
import '@carbon/charts-react/styles.css';
import useThemeStore from '../../store/useThemeStore';
import { APP_SHELL_BASE } from '../../constants/appConstants';
import { useCarbonChartTheme } from '../../hooks/useCarbonChartTheme';
import { useTypewriter } from '../../hooks/useTypewriter';
import './Landing.scss';

const demoHref = `${APP_SHELL_BASE}/pull-requests`;
const dashboardHref = `${APP_SHELL_BASE}/dashboard`;

const beforeAfterChartData = [
  { group: 'Time to first actionable review', key: 'Typical manual loop', value: 24 },
  { group: 'Time to first actionable review', key: 'IBM Dexter', value: 2 },
  { group: 'Org standards cited in review', key: 'Typical manual loop', value: 2 },
  { group: 'Org standards cited in review', key: 'IBM Dexter', value: 14 },
  { group: 'Delivery risk signals surfaced', key: 'Typical manual loop', value: 4 },
  { group: 'Delivery risk signals surfaced', key: 'IBM Dexter', value: 17 },
];

const sectionFade = {
  initial: { opacity: 0, y: 28 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: '-40px' },
  transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] },
};

const stagger = {
  visible: {
    transition: { staggerChildren: 0.08 },
  },
};

const itemFade = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45 } },
};

const Landing = () => {
  const { theme, toggleTheme } = useThemeStore();
  const chartTheme = useCarbonChartTheme();
  useLayoutEffect(() => {
    document.documentElement.setAttribute('data-carbon-theme', theme);
  }, [theme]);

  const typePhrases = useMemo(
    () => [
      'The same depth as a Staff+ review — at software speed.',
      'Turning every PR into institutional memory — not just a green check.',
      'Governance, architecture, and security — orchestrated as enterprise intelligence.',
      'Your playbooks, policies, and history — on every line of the diff.',
    ],
    []
  );
  const typedLine = useTypewriter(typePhrases, { typingMs: 38, pauseMs: 2800 });

  const groupedBarOptions = useMemo(
    () => ({
      title: 'Delivery intelligence: illustrative before / after',
      axes: {
        left: {
          mapsTo: 'value',
          title: 'Index (normalized)',
          scaleType: 'linear',
        },
        bottom: {
          title: 'Measure',
          mapsTo: 'group',
          scaleType: 'labels',
        },
      },
      height: '340px',
      theme: chartTheme,
    }),
    [chartTheme]
  );

  return (
    <Theme theme={theme}>
      <div className="dexter-landing" data-carbon-theme={theme}>
        <SkipToContent href="#dexter-main">Skip to main content</SkipToContent>

        <Header aria-label="IBM Dexter" className="dexter-landing__header">
          <HeaderName href="/" prefix="IBM">
            Dexter
          </HeaderName>
          <HeaderNavigation aria-label="Product">
            <HeaderMenuItem href="#enterprise-intelligence">Enterprise intelligence</HeaderMenuItem>
            <HeaderMenuItem href="#before-after">Before & after</HeaderMenuItem>
            <HeaderMenuItem href="#platform">Platform</HeaderMenuItem>
            <HeaderMenuItem href="#senior-review">Senior review</HeaderMenuItem>
          </HeaderNavigation>
          <HeaderGlobalBar>
            <HeaderGlobalAction
              aria-label={`Switch to ${theme === 'g100' ? 'light' : 'dark'} theme`}
              onClick={toggleTheme}
              tooltipAlignment="end"
            >
              {theme === 'g100' ? <Light size={20} /> : <Asleep size={20} />}
            </HeaderGlobalAction>
            <div className="dexter-landing__header-cta">
              <Link to={dashboardHref} className="dexter-landing__link-btn">
                <Button kind="primary" size="md">
                  Launch demo
                </Button>
              </Link>
            </div>
          </HeaderGlobalBar>
        </Header>

        <header className="dexter-landing__hero" id="dexter-main">
          <div className="dexter-landing__hero-bg" aria-hidden />
          <motion.div
            className="dexter-landing__hero-inner"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          >
            <motion.img
              className="dexter-landing__hero-logo"
              src="/Dexter_logo.png"
              alt="IBM Dexter"
              width={120}
              height={120}
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
            />
            <p className="dexter-landing__eyebrow">
              <UserSpeaker size={16} aria-hidden className="dexter-landing__eyebrow-icon" />
              IBM Engineering · Enterprise intelligence layer
            </p>
            <h1 className="dexter-landing__title">This is not another PR bot.</h1>
            <p className="dexter-landing__lead dexter-landing__lead--strong">
              Dexter is the <strong>future of enterprise intelligence</strong> for software delivery — where code
              review, organizational knowledge, and governance meet in one continuous system. Not a comment thread with
              a model behind it: a governed, explainable layer that scales how your best engineers think.
            </p>
            <p className="dexter-landing__typewriter" aria-live="polite">
              <span className="dexter-landing__typewriter-label">Senior engineer bar, on every PR:</span>{' '}
              <span className="dexter-landing__typewriter-text">
                {typedLine}
                <span className="dexter-landing__cursor" aria-hidden>
                  |
                </span>
              </span>
            </p>
            <div className="dexter-landing__cta-row">
              <Link to={dashboardHref} className="dexter-landing__link-btn">
                <Button kind="primary" size="lg" renderIcon={ArrowRight}>
                  Open the intelligence console
                </Button>
              </Link>
              <Link to={demoHref} className="dexter-landing__link-btn">
                <Button kind="secondary" size="lg" renderIcon={LogoGithub}>
                  Analyze a GitHub PR
                </Button>
              </Link>
            </div>
          </motion.div>
        </header>

        <section className="dexter-landing__section dexter-landing__section--intel" id="enterprise-intelligence">
          <motion.div {...sectionFade}>
            <Grid narrow className="dexter-landing__grid">
              <Column lg={16} md={8} sm={4}>
                <h2>Enterprise intelligence — not “AI slop on a diff”</h2>
                <p className="dexter-landing__prose">
                  Generic code reviewers optimize for plausible sentences. Dexter is built for{' '}
                  <strong>traceability</strong>: multi-agent analysis, structured findings, optional inline suggestions,
                  RAG over <em>your</em> standards and runbooks, and routing into GitHub as real reviews — so outcomes
                  are auditable like any other enterprise control. That is the difference between a tool and a{' '}
                  <strong>capability layer</strong> for regulated, high-stakes engineering.
                </p>
              </Column>
            </Grid>
          </motion.div>
        </section>

        <section className="dexter-landing__section dexter-landing__section--alt" id="before-after">
          <motion.div {...sectionFade}>
            <Grid narrow>
              <Column lg={8} md={4} sm={4}>
                <h2>Before / after the intelligence layer</h2>
                <p className="dexter-landing__prose">
                  The chart is <strong>illustrative</strong> — your metrics come from real runs in the dashboard —
                  but the pattern is what enterprises care about: faster signal, richer alignment to policy, and more
                  delivery risk caught before merge — without waiting for the same small set of senior reviewers to
                  become bottlenecks.
                </p>
                <ul className="dexter-landing__bullets">
                  <li>Manual loops depend on calendar time, context switching, and tribal knowledge.</li>
                  <li>Dexter encodes repeatability: agents, KB, and integrations as a single workflow.</li>
                </ul>
              </Column>
              <Column lg={8} md={4} sm={4}>
                <Tile className="dexter-landing__chart-tile">
                  <GroupedBarChart data={beforeAfterChartData} options={groupedBarOptions} />
                </Tile>
              </Column>
            </Grid>
          </motion.div>
        </section>

        <section className="dexter-landing__section" id="senior-review">
          <motion.div {...sectionFade}>
            <Grid narrow>
              <Column lg={16}>
                <Tile className="dexter-landing__quote-tile">
                  <UserSpeaker size={32} className="dexter-landing__quote-icon" aria-hidden />
                  <blockquote className="dexter-landing__quote">
                    “We did not need faster opinions. We needed <strong>consistent senior judgement</strong>, bound to our
                    architecture standards and security posture — without burning out the team that already carries it
                    in their heads. That is the bar Dexter is designed for.”
                  </blockquote>
                  <cite className="dexter-landing__cite">
                    — Representative enterprise engineering lead (composite narrative for product positioning)
                  </cite>
                </Tile>
              </Column>
            </Grid>
          </motion.div>
        </section>

        <motion.section
          className="dexter-landing__section dexter-landing__section--tiles"
          id="platform"
          variants={stagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
        >
          <Grid narrow className="dexter-landing__grid">
            <Column lg={16} md={8} sm={4}>
              <h2>Platform capabilities</h2>
              <p className="dexter-landing__muted">
                Security, architecture, compliance — plus knowledge base RAG, GitHub automation, and ops visibility.
              </p>
            </Column>
            <Column lg={4} md={4} sm={4}>
              <motion.div variants={itemFade}>
                <Tile className="dexter-landing__tile dexter-landing__tile--glow">
                  <Security size={32} />
                  <h3>Security &amp; compliance</h3>
                  <p>
                    Deterministic pre-filtering plus LLM reasoning — structured JSON, severity, optional inline
                    fixes — not vibes.
                  </p>
                </Tile>
              </motion.div>
            </Column>
            <Column lg={4} md={4} sm={4}>
              <motion.div variants={itemFade}>
                <Tile className="dexter-landing__tile dexter-landing__tile--glow">
                  <Bot size={32} />
                  <h3>Multi-agent orchestration</h3>
                  <p>
                    Coordinated agents share context so architecture and policy questions do not get answered in
                    isolation.
                  </p>
                </Tile>
              </motion.div>
            </Column>
            <Column lg={4} md={4} sm={4}>
              <motion.div variants={itemFade}>
                <Tile className="dexter-landing__tile dexter-landing__tile--glow">
                  <Book size={32} />
                  <h3>Knowledge base RAG</h3>
                  <p>
                    PDFs, DOCX, runbooks — chunked, embedded, retrieved at review time so feedback cites{' '}
                    <em>your</em> org.
                  </p>
                </Tile>
              </motion.div>
            </Column>
            <Column lg={4} md={4} sm={4}>
              <motion.div variants={itemFade}>
                <Tile className="dexter-landing__tile dexter-landing__tile--glow">
                  <Flash size={32} />
                  <h3>Delivery automation</h3>
                  <p>
                    Webhook-driven reviews, reviewer assignment, PR comments with Dexter branding — automation that
                    still reads as engineering rigor.
                  </p>
                </Tile>
              </motion.div>
            </Column>
          </Grid>
        </motion.section>

        <section className="dexter-landing__section dexter-landing__section--alt">
          <motion.div {...sectionFade}>
            <Grid narrow>
              <Column lg={8} md={4} sm={4}>
                <h2>How teams adopt it</h2>
                <ol className="dexter-landing__steps">
                  <li>Connect your model stack (e.g. Ollama) and GitHub in Settings — tokens stay under your control.</li>
                  <li>Ingest standards, threat models, and internal patterns into the knowledge base.</li>
                  <li>Register repositories for <strong>auto-review</strong> — or run live analysis on any public PR.</li>
                </ol>
                <Link to={demoHref} className="dexter-landing__inline-link">
                  <Button kind="tertiary" renderIcon={ArrowRight}>
                    Try live PR analysis
                  </Button>
                </Link>
              </Column>
              <Column lg={8} md={4} sm={4}>
                <Tile className="dexter-landing__tile">
                  <LogoGithub size={28} />
                  <h3>GitHub as a first-class surface</h3>
                  <p>
                    Fetch diffs, attach inline suggestions where the model supports them, post a branded summary review,
                    and request reviewers — so intelligence shows up where developers already work.
                  </p>
                </Tile>
              </Column>
            </Grid>
          </motion.div>
        </section>

        <section className="dexter-landing__section">
          <motion.div {...sectionFade}>
            <Grid narrow>
              <Column lg={16} md={8} sm={4}>
                <h2>Measurement &amp; trust</h2>
                <p className="dexter-landing__muted">
                  Dashboards connect to real backend activity — trends, severity, architecture hints — so leaders see
                  adoption, not toy metrics.
                </p>
              </Column>
              <Column lg={8} md={4} sm={4}>
                <Tile className="dexter-landing__tile">
                  <ChartLine size={28} />
                  <h3>Visibility</h3>
                  <p>Review activity, findings distribution, and signals from real agent runs.</p>
                  <Link to={dashboardHref} className="dexter-landing__inline-link">
                    <Button kind="ghost" size="sm">
                      View dashboard
                    </Button>
                  </Link>
                </Tile>
              </Column>
              <Column lg={8} md={4} sm={4}>
                <Tile className="dexter-landing__tile">
                  <Settings size={28} />
                  <h3>Governed configuration</h3>
                  <p>Model choice, integrations, and embeddings persist locally between restarts.</p>
                  <Link to={`${APP_SHELL_BASE}/settings`} className="dexter-landing__inline-link">
                    <Button kind="ghost" size="sm">
                      Open settings
                    </Button>
                  </Link>
                </Tile>
              </Column>
            </Grid>
          </motion.div>
        </section>

        <section className="dexter-landing__section dexter-landing__section--cta">
          <motion.div {...sectionFade}>
            <Grid narrow>
              <Column lg={16}>
                <Tile className="dexter-landing__cta-tile">
                  <h2>Bring senior judgement to every merge — at scale</h2>
                  <p>
                    Launch the full Carbon experience locally — wire your org knowledge — and treat code review as{' '}
                    <strong>intelligence infrastructure</strong>, not a side chat.
                  </p>
                  <Link to={dashboardHref} className="dexter-landing__link-btn">
                    <Button kind="primary" size="lg" renderIcon={ArrowRight}>
                      Enter Dexter
                    </Button>
                  </Link>
                </Tile>
              </Column>
            </Grid>
          </motion.div>
        </section>

        <footer className="dexter-landing__footer">
          <div className="dexter-landing__footer-inner">
            <img src="/Dexter_logo.png" alt="" width={40} height={40} />
            <span>IBM Dexter · Enterprise intelligence for software engineering</span>
          </div>
        </footer>
      </div>
    </Theme>
  );
};

export default Landing;
