
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class TicketUtils:
    """Utility functions for ticket processing"""
    
    @staticmethod
    def calculate_ticket_age(timestamp: int) -> Dict:
        """Calculate ticket age in various units"""
        current_time = datetime.now().timestamp()
        age_seconds = current_time - timestamp
        
        return {
            'seconds': age_seconds,
            'minutes': age_seconds / 60,
            'hours': age_seconds / 3600,
            'days': age_seconds / 86400,
            'age_category': TicketUtils._categorize_age(age_seconds / 3600)
        }
    
    @staticmethod
    def _categorize_age(hours: float) -> str:
        """Categorize ticket age"""
        if hours < 1:
            return 'new'
        elif hours < 4:
            return 'recent'
        elif hours < 24:
            return 'pending'
        elif hours < 72:
            return 'aging'
        else:
            return 'overdue'
    
    @staticmethod
    def extract_entities(text: str) -> Dict:
        """Extract entities from ticket text"""
        entities = {
            'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text),
            'ip_addresses': re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', text),
            'urls': re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text),
            'ticket_refs': re.findall(r'TKT-\d{4}-\d{3}', text),
            'error_codes': re.findall(r'(?:error|code)\s*:?\s*([0-9A-Fx]+)', text, re.IGNORECASE),
            'file_paths': re.findall(r'(?:[A-Z]:)?[\\/](?:[^\\/\s]+[\\/])*[^\\/\s]+', text)
        }
        return entities
    
    @staticmethod
    def calculate_text_complexity(text: str) -> float:
        """Calculate text complexity score"""
        words = text.split()
        if not words:
            return 0
        
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        technical_terms = [
            'api', 'sql', 'dns', 'vpn', 'ssl', 'tcp', 'udp', 'http', 'https',
            'cpu', 'ram', 'gpu', 'ssd', 'hdd', 'raid', 'backup', 'restore'
        ]
        tech_count = sum(1 for term in technical_terms if term in text.lower())
        
        complexity = (
            (avg_word_length / 5) * 0.3 +
            (len(words) / 100) * 0.3 +
            (sentence_count / 10) * 0.2 +
            (tech_count / 5) * 0.2
        )
        
        return min(complexity, 1.0)
    
    @staticmethod
    def generate_ticket_hash(ticket: Dict) -> str:
        """Generate unique hash for ticket"""
        content = f"{ticket.get('ticket_id', '')}{ticket.get('title', '')}{ticket.get('description', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    @staticmethod
    def detect_duplicate_tickets(tickets: List[Dict], threshold: float = 0.8) -> List[List[str]]:
        """Detect potential duplicate tickets"""
        duplicates = []
        processed = set()
        
        for i, ticket1 in enumerate(tickets):
            if ticket1['ticket_id'] in processed:
                continue
                
            similar_group = [ticket1['ticket_id']]
            
            for j, ticket2 in enumerate(tickets[i+1:], i+1):
                if ticket2['ticket_id'] in processed:
                    continue
                
                text1 = f"{ticket1.get('title', '')} {ticket1.get('description', '')}"
                text2 = f"{ticket2.get('title', '')} {ticket2.get('description', '')}"
                
                words1 = set(text1.lower().split())
                words2 = set(text2.lower().split())
                
                if words1 and words2:
                    intersection = words1.intersection(words2)
                    union = words1.union(words2)
                    similarity = len(intersection) / len(union)
                    
                    if similarity >= threshold:
                        similar_group.append(ticket2['ticket_id'])
                        processed.add(ticket2['ticket_id'])
            
            if len(similar_group) > 1:
                duplicates.append(similar_group)
                processed.add(ticket1['ticket_id'])
        
        return duplicates


class AgentUtils:
    """Utility functions for agent management"""
    
    @staticmethod
    def calculate_agent_capacity(agent: Dict, config: Dict) -> Dict:
        """Calculate agent's remaining capacity"""
        max_load = config.get('max_load_per_agent', 10)
        current_load = agent.get('current_load', 0)
        
        capacity = {
            'current_load': current_load,
            'max_load': max_load,
            'remaining_capacity': max_load - current_load,
            'utilization_percentage': (current_load / max_load) * 100,
            'is_available': agent.get('availability_status') == 'Available',
            'can_accept_more': current_load < max_load
        }
        
        if capacity['utilization_percentage'] >= 90:
            capacity['status'] = 'overloaded'
        elif capacity['utilization_percentage'] >= 70:
            capacity['status'] = 'busy'
        elif capacity['utilization_percentage'] >= 40:
            capacity['status'] = 'moderate'
        else:
            capacity['status'] = 'available'
        
        return capacity
    
    @staticmethod
    def find_backup_agents(primary_agent: Dict, all_agents: Dict, 
                          required_skills: List[str]) -> List[Tuple[str, float]]:
        """Find backup agents for a primary agent"""
        backups = []
        
        for agent_id, agent in all_agents.items():
            if agent_id == primary_agent.get('agent_id'):
                continue
            
            overlap_score = 0
            for skill in required_skills:
                if skill in agent.get('skills', {}):
                    overlap_score += agent['skills'][skill]
            
            if overlap_score > 0:
                final_score = overlap_score * 0.6
                if agent.get('availability_status') == 'Available':
                    final_score += 20
                final_score += agent.get('experience_level', 0) * 0.5
                
                backups.append((agent_id, final_score))
        
        backups.sort(key=lambda x: x[1], reverse=True)
        return backups[:3]
    
    @staticmethod
    def calculate_team_balance(agents: Dict) -> Dict:
        """Calculate team balance metrics"""
        if not agents:
            return {}
        
        workloads = [agent.get('current_load', 0) for agent in agents.values()]
        experiences = [agent.get('experience_level', 0) for agent in agents.values()]
        
        balance_metrics = {
            'workload_stats': {
                'mean': statistics.mean(workloads) if workloads else 0,
                'median': statistics.median(workloads) if workloads else 0,
                'stdev': statistics.stdev(workloads) if len(workloads) > 1 else 0,
                'min': min(workloads) if workloads else 0,
                'max': max(workloads) if workloads else 0
            },
            'experience_stats': {
                'mean': statistics.mean(experiences) if experiences else 0,
                'median': statistics.median(experiences) if experiences else 0,
                'min': min(experiences) if experiences else 0,
                'max': max(experiences) if experiences else 0
            },
            'balance_score': 0
        }
        
        if len(workloads) > 1:
            balance_metrics['balance_score'] = balance_metrics['workload_stats']['stdev']
        
        if balance_metrics['balance_score'] < 1:
            balance_metrics['balance_category'] = 'excellent'
        elif balance_metrics['balance_score'] < 2:
            balance_metrics['balance_category'] = 'good'
        elif balance_metrics['balance_score'] < 3:
            balance_metrics['balance_category'] = 'fair'
        else:
            balance_metrics['balance_category'] = 'poor'
        
        return balance_metrics


class ReportGenerator:
    """Generate various reports for the system"""
    
    @staticmethod
    def generate_summary_report(assignments: List[Dict], agents: Dict, 
                               tickets: Dict) -> str:
        """Generate executive summary report"""
        report = []
        report.append("="*60)
        report.append("EXECUTIVE SUMMARY - TICKET ASSIGNMENT SYSTEM")
        report.append("="*60)
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        total_tickets = len(tickets)
        assigned_count = sum(1 for a in assignments if a.get('assigned_agent_id'))
        success_rate = (assigned_count / total_tickets * 100) if total_tickets > 0 else 0
        
        priority_counts = defaultdict(int)
        for assignment in assignments:
            priority_counts[assignment.get('priority', 'UNKNOWN')] += 1
        
        report.append("KEY METRICS:")
        report.append(f"  • Total Tickets: {total_tickets}")
        report.append(f"  • Successfully Assigned: {assigned_count} ({success_rate:.1f}%)")
        report.append(f"  • Unassigned: {total_tickets - assigned_count}")
        report.append("")
        
        report.append("PRIORITY DISTRIBUTION:")
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = priority_counts.get(priority, 0)
            percentage = (count / total_tickets * 100) if total_tickets > 0 else 0
            report.append(f"  • {priority}: {count} ({percentage:.1f}%)")
        report.append("")
        
        agent_utils = AgentUtils()
        utilizations = []
        for agent in agents.values():
            capacity = agent_utils.calculate_agent_capacity(agent, {'max_load_per_agent': 10})
            utilizations.append(capacity['utilization_percentage'])
        
        if utilizations:
            report.append("AGENT UTILIZATION:")
            report.append(f"  • Average: {statistics.mean(utilizations):.1f}%")
            report.append(f"  • Highest: {max(utilizations):.1f}%")
            report.append(f"  • Lowest: {min(utilizations):.1f}%")
        
        report.append("")
        report.append("="*60)
        
        return '\n'.join(report)
    
    @staticmethod
    def generate_agent_report(agent_id: str, agent: Dict, 
                             assignments: List[Dict]) -> str:
        """Generate individual agent report"""
        agent_assignments = [a for a in assignments 
                           if a.get('assigned_agent_id') == agent_id]
        
        report = []
        report.append(f"AGENT REPORT: {agent.get('name', 'Unknown')}")
        report.append("-"*40)
        report.append(f"Agent ID: {agent_id}")
        report.append(f"Experience Level: {agent.get('experience_level', 0)}")
        report.append(f"Current Load: {agent.get('current_load', 0)}")
        report.append(f"Total Assigned: {len(agent_assignments)}")
        report.append("")
        
        report.append("TOP SKILLS:")
        skills = agent.get('skills', {})
        top_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:5]
        for skill, level in top_skills:
            report.append(f"  • {skill}: {level}/10")
        report.append("")
        
        report.append("ASSIGNED TICKETS BY PRIORITY:")
        priority_counts = defaultdict(int)
        for assignment in agent_assignments:
            priority_counts[assignment.get('priority', 'UNKNOWN')] += 1
        
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = priority_counts.get(priority, 0)
            if count > 0:
                report.append(f"  • {priority}: {count}")
        
        return '\n'.join(report)


def validate_data(data_path: str) -> Tuple[bool, List[str]]:
    """Validate input data structure"""
    errors = []
    
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        if 'agents' not in data:
            errors.append("Missing 'agents' key in data")
        if 'tickets' not in data:
            errors.append("Missing 'tickets' key in data")
        
        if 'agents' in data:
            for i, agent in enumerate(data['agents']):
                if 'agent_id' not in agent:
                    errors.append(f"Agent {i} missing 'agent_id'")
                if 'skills' not in agent:
                    errors.append(f"Agent {i} missing 'skills'")
        
        if 'tickets' in data:
            for i, ticket in enumerate(data['tickets']):
                if 'ticket_id' not in ticket:
                    errors.append(f"Ticket {i} missing 'ticket_id'")
                if 'description' not in ticket:
                    errors.append(f"Ticket {i} missing 'description'")
        
    except Exception as e:
        errors.append(f"Error loading data: {str(e)}")
    
    return len(errors) == 0, errors
