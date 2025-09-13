"""
Machine Learning Enhanced Ticket Classification Module
Uses TF-IDF and similarity scoring for better ticket understanding
"""

import json
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
from pathlib import Path


class MLTicketClassifier:
    """
    Advanced ML-based ticket classification system
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.8
        )
        self.skill_vectors = None
        self.category_patterns = self._initialize_patterns()
        self.historical_patterns = defaultdict(list)
        
    def _initialize_patterns(self) -> Dict:
        """Initialize regex patterns for ticket categorization"""
        return {
            'network': {
                'patterns': [
                    r'\b(network|connection|connectivity|lan|wan|ethernet|wifi|wireless)\b',
                    r'\b(router|switch|firewall|vpn|dns|dhcp|ip\s+address)\b',
                    r'\b(ping|traceroute|packet\s+loss|latency|bandwidth)\b'
                ],
                'severity_indicators': ['down', 'outage', 'unreachable', 'timeout']
            },
            'security': {
                'patterns': [
                    r'\b(security|breach|attack|malware|virus|phishing|ransomware)\b',
                    r'\b(unauthorized|suspicious|compromised|infected|vulnerability)\b',
                    r'\b(firewall|antivirus|encryption|ssl|tls|certificate)\b'
                ],
                'severity_indicators': ['breach', 'attack', 'compromised', 'critical']
            },
            'hardware': {
                'patterns': [
                    r'\b(hardware|laptop|desktop|computer|pc|server|device)\b',
                    r'\b(screen|monitor|keyboard|mouse|printer|scanner)\b',
                    r'\b(fan|battery|power|boot|bios|memory|ram|disk|ssd|hdd)\b'
                ],
                'severity_indicators': ['broken', 'failed', 'dead', 'not working']
            },
            'software': {
                'patterns': [
                    r'\b(software|application|app|program|install|update|patch)\b',
                    r'\b(windows|linux|macos|office|outlook|teams|sharepoint)\b',
                    r'\b(error|crash|freeze|hang|slow|performance)\b'
                ],
                'severity_indicators': ['crash', 'critical error', 'data loss']
            },
            'database': {
                'patterns': [
                    r'\b(database|sql|query|table|schema|backup|restore)\b',
                    r'\b(mysql|postgresql|mssql|oracle|mongodb|redis)\b',
                    r'\b(performance|optimization|index|deadlock|timeout)\b'
                ],
                'severity_indicators': ['corruption', 'data loss', 'production']
            },
            'cloud': {
                'patterns': [
                    r'\b(cloud|aws|azure|gcp|kubernetes|docker|container)\b',
                    r'\b(ec2|s3|lambda|vm|instance|deployment|pipeline)\b',
                    r'\b(scaling|availability|region|zone|cdn)\b'
                ],
                'severity_indicators': ['outage', 'down', 'unavailable']
            }
        }
    
    def extract_features(self, text: str) -> Dict:
        """Extract comprehensive features from ticket text"""
        features = {
            'length': len(text),
            'word_count': len(text.split()),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / max(len(text), 1),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'categories': [],
            'severity_score': 0,
            'technical_terms': []
        }
        
        for category, config in self.category_patterns.items():
            category_score = 0
            for pattern in config['patterns']:
                if re.search(pattern, text.lower()):
                    category_score += 1
            
            if category_score > 0:
                features['categories'].append((category, category_score))
                
                for indicator in config['severity_indicators']:
                    if indicator in text.lower():
                        features['severity_score'] += 2
        
        technical_keywords = [
            'api', 'sql', 'dns', 'vpn', 'ssl', 'tcp', 'udp', 'http', 'https',
            'cpu', 'ram', 'gpu', 'ssd', 'hdd', 'raid', 'backup', 'restore',
            'firewall', 'proxy', 'cache', 'cluster', 'node', 'pod', 'container'
        ]
        
        for term in technical_keywords:
            if term in text.lower():
                features['technical_terms'].append(term)
        
        return features
    
    def train_skill_model(self, tickets: List[Dict], agents: List[Dict]):
        """Train the skill matching model using historical data"""
        skill_descriptions = []
        skill_labels = []
        
        skill_templates = {
            'Networking': 'network connectivity vpn connection router switch firewall configuration',
            'Database_SQL': 'database sql query performance optimization table index backup restore',
            'Cloud_AWS': 'aws cloud ec2 s3 lambda serverless infrastructure deployment',
            'Security': 'security breach attack malware virus phishing authentication encryption',
            'Hardware_Diagnostics': 'hardware laptop desktop computer fan battery power boot bios',
            'Windows_OS': 'windows operating system registry driver update patch installation',
            'Linux_Administration': 'linux ubuntu debian centos bash shell script permissions',
            'Microsoft_365': 'microsoft office outlook teams sharepoint onedrive email calendar'
        }
        
        for skill, description in skill_templates.items():
            skill_descriptions.append(description)
            skill_labels.append(skill)
        
        if skill_descriptions:
            self.skill_vectors = self.vectorizer.fit_transform(skill_descriptions)
            self.skill_labels = skill_labels
    
    def predict_required_skills(self, ticket_text: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """Predict required skills for a ticket using ML"""
        if self.skill_vectors is None:
            return []
        
        ticket_vector = self.vectorizer.transform([ticket_text])
        
        similarities = cosine_similarity(ticket_vector, self.skill_vectors)[0]
        
        top_indices = np.argsort(similarities)[-top_n:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                results.append((self.skill_labels[idx], float(similarities[idx])))
        
        return results
    
    def calculate_complexity_score(self, ticket: Dict) -> float:
        """Calculate ticket complexity using multiple factors"""
        text = f"{ticket.get('title', '')} {ticket.get('description', '')}"
        features = self.extract_features(text)
        
        complexity = 0
        
        if features['word_count'] > 200:
            complexity += 2
        elif features['word_count'] > 100:
            complexity += 1
        
        complexity += len(features['technical_terms']) * 0.5
        
        if len(features['categories']) > 2:
            complexity += 2
        elif len(features['categories']) > 1:
            complexity += 1
        
        complexity += features['severity_score'] * 0.3
        
        complexity += features['question_count'] * 0.2
        
        return min(complexity, 10)
    
    def find_similar_tickets(self, ticket: Dict, historical_tickets: List[Dict], 
                            top_n: int = 3) -> List[Dict]:
        """Find similar historical tickets for better assignment"""
        if not historical_tickets:
            return []
        
        current_text = f"{ticket.get('title', '')} {ticket.get('description', '')}"
        historical_texts = [f"{t.get('title', '')} {t.get('description', '')}" 
                          for t in historical_tickets]
        
        all_texts = [current_text] + historical_texts
        
        try:
            vectors = self.vectorizer.fit_transform(all_texts)
            current_vector = vectors[0]
            historical_vectors = vectors[1:]
            
            similarities = cosine_similarity(current_vector, historical_vectors)[0]
            
            top_indices = np.argsort(similarities)[-top_n:][::-1]
            
            similar_tickets = []
            for idx in top_indices:
                if similarities[idx] > 0.3:
                    similar_tickets.append({
                        'ticket': historical_tickets[idx],
                        'similarity': float(similarities[idx])
                    })
            
            return similar_tickets
        except:
            return []
    
    def save_model(self, path: str = 'ml_model.pkl'):
        """Save the trained model"""
        model_data = {
            'vectorizer': self.vectorizer,
            'skill_vectors': self.skill_vectors,
            'skill_labels': getattr(self, 'skill_labels', []),
            'historical_patterns': dict(self.historical_patterns)
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, path: str = 'ml_model.pkl'):
        """Load a trained model"""
        if Path(path).exists():
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
                self.vectorizer = model_data['vectorizer']
                self.skill_vectors = model_data['skill_vectors']
                self.skill_labels = model_data.get('skill_labels', [])
                self.historical_patterns = defaultdict(list, model_data.get('historical_patterns', {}))
                return True
        return False
    