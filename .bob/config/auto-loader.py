#!/usr/bin/env python3
"""
BOB AI Skill Auto-Loader
Automatically loads relevant skills based on user prompts and context.
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set


class SkillAutoLoader:
    """Intelligent skill loader for BOB AI"""
    
    def __init__(self, config_path: str = ".bob/config/skill-loader.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.usage_log = []
        self.loaded_skills = set()
        
    def _load_config(self) -> Dict:
        """Load skill loader configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def analyze_prompt(self, prompt: str) -> List[str]:
        """
        Analyze user prompt and identify relevant skills
        
        Args:
            prompt: User's input prompt
            
        Returns:
            List of skill identifiers that match the prompt
        """
        prompt_lower = prompt.lower()
        matched_skills = set()
        
        # Check each trigger pattern
        for pattern, skills in self.config.get("prompt_triggers", {}).items():
            # Split pattern by | to get individual keywords
            keywords = pattern.split("|")
            
            # Check if any keyword matches
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword.strip()) + r'\b', prompt_lower):
                    matched_skills.update(skills)
                    break
        
        return list(matched_skills)
    
    def load_skill(self, skill_id: str) -> Dict:
        """
        Load a specific skill by ID
        
        Args:
            skill_id: Skill identifier from skill_mapping
            
        Returns:
            Dictionary containing skill information
        """
        skill_mapping = self.config.get("skill_mapping", {})
        
        if skill_id not in skill_mapping:
            raise ValueError(f"Unknown skill ID: {skill_id}")
        
        skill_path = Path(skill_mapping[skill_id])
        
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill file not found: {skill_path}")
        
        with open(skill_path, 'r') as f:
            skill_content = f.read()
        
        self.loaded_skills.add(skill_id)
        self._log_usage(skill_id, str(skill_path))
        
        return {
            "id": skill_id,
            "path": str(skill_path),
            "content": skill_content,
            "loaded_at": datetime.now().isoformat()
        }
    
    def load_skills_for_prompt(self, prompt: str) -> List[Dict]:
        """
        Analyze prompt and load all relevant skills
        
        Args:
            prompt: User's input prompt
            
        Returns:
            List of loaded skill dictionaries
        """
        skill_ids = self.analyze_prompt(prompt)
        loaded = []
        
        for skill_id in skill_ids:
            try:
                skill = self.load_skill(skill_id)
                loaded.append(skill)
            except Exception as e:
                print(f"Warning: Failed to load skill {skill_id}: {e}")
        
        return loaded
    
    def get_skill_recommendations(self, prompt: str) -> Dict:
        """
        Get skill recommendations without loading them
        
        Args:
            prompt: User's input prompt
            
        Returns:
            Dictionary with recommendations and confidence scores
        """
        skill_ids = self.analyze_prompt(prompt)
        recommendations = []
        
        for skill_id in skill_ids:
            skill_path = self.config["skill_mapping"].get(skill_id, "")
            recommendations.append({
                "skill_id": skill_id,
                "path": skill_path,
                "already_loaded": skill_id in self.loaded_skills
            })
        
        return {
            "prompt": prompt,
            "recommended_skills": recommendations,
            "count": len(recommendations)
        }
    
    def _log_usage(self, skill_id: str, skill_path: str):
        """Log skill usage for analytics"""
        self.usage_log.append({
            "skill_id": skill_id,
            "path": skill_path,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_usage_stats(self) -> Dict:
        """Get skill usage statistics"""
        stats = {}
        for entry in self.usage_log:
            skill_id = entry["skill_id"]
            stats[skill_id] = stats.get(skill_id, 0) + 1
        
        return {
            "total_loads": len(self.usage_log),
            "unique_skills": len(stats),
            "skill_counts": stats,
            "currently_loaded": list(self.loaded_skills)
        }
    
    def list_all_skills(self) -> List[Dict]:
        """List all available skills"""
        skills = []
        for skill_id, path in self.config.get("skill_mapping", {}).items():
            skills.append({
                "id": skill_id,
                "path": path,
                "exists": Path(path).exists(),
                "loaded": skill_id in self.loaded_skills
            })
        return skills
    
    def auto_load_for_context(self, context: str) -> List[Dict]:
        """
        Automatically load skills based on project context
        
        Args:
            context: Project context or description
            
        Returns:
            List of auto-loaded skills
        """
        if not self.config.get("auto_load", False):
            return []
        
        return self.load_skills_for_prompt(context)


def main():
    """CLI interface for skill auto-loader"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python auto-loader.py <command> [args]")
        print("\nCommands:")
        print("  analyze <prompt>     - Analyze prompt and show recommendations")
        print("  load <prompt>        - Load skills for prompt")
        print("  list                 - List all available skills")
        print("  stats                - Show usage statistics")
        return
    
    loader = SkillAutoLoader()
    command = sys.argv[1]
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print("Error: Please provide a prompt to analyze")
            return
        prompt = " ".join(sys.argv[2:])
        recommendations = loader.get_skill_recommendations(prompt)
        print(json.dumps(recommendations, indent=2))
    
    elif command == "load":
        if len(sys.argv) < 3:
            print("Error: Please provide a prompt")
            return
        prompt = " ".join(sys.argv[2:])
        skills = loader.load_skills_for_prompt(prompt)
        print(f"Loaded {len(skills)} skills:")
        for skill in skills:
            print(f"  - {skill['id']} ({skill['path']})")
    
    elif command == "list":
        skills = loader.list_all_skills()
        print(f"Available skills ({len(skills)}):")
        for skill in skills:
            status = "✓ loaded" if skill['loaded'] else ("✓ available" if skill['exists'] else "✗ missing")
            print(f"  {status} {skill['id']}: {skill['path']}")
    
    elif command == "stats":
        stats = loader.get_usage_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()

# Made with Bob
