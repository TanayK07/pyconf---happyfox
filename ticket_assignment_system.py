#!/usr/bin/env python3
"""
Intelligent Support Ticket Assignment System
PyCon25 Hackathon Project
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import heapq
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TicketPriority:
    """Data class for ticket priority calculation"""
    ticket_id: str
    priority_score: float
    urgency_level: str
    business_impact: float
    affected_users: int
    security_risk: float
    
    def __lt__(self, other):
        return self.priority_score > other.priority_score


class AdvancedTicketAssignmentSystem:
    """
    Advanced ticket assignment system with ML-inspired features,
    intelligent routing, and comprehensive business logic.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.agents = {}
        self.tickets = {}
        self.assignments = []
        self.config = self._load_config(config_path)
        self.skill_requirements_cache = {}
        self.agent_performance_history = defaultdict(lambda: {
            'resolved': 0, 'total': 0, 'avg_resolution_time': 0
        })
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load system configuration"""
        default_config = {
            'max_load_per_agent': 10,
            'skill_match_weight': 0.4,
            'experience_weight': 0.2,
            'workload_weight': 0.2,
            'priority_weight': 0.2,
            'critical_keywords': [
                'critical', 'urgent', 'down', 'outage', 'security', 
                'breach', 'attack', 'production', 'business-critical'
            ],
            'high_priority_keywords': [
                'failing', 'error', 'unable', 'blocked', 'stopped'
            ],
            'skill_categories': {
                'networking': ['Networking', 'VPN_Troubleshooting', 'Network_Security', 
                              'Network_Monitoring', 'Network_Cabling', 'DNS_Configuration'],
                'security': ['Network_Security', 'Endpoint_Security', 'Antivirus_Malware',
                            'Phishing_Analysis', 'Security_Audits', 'SIEM_Logging'],
                'hardware': ['Hardware_Diagnostics', 'Laptop_Repair', 'Printer_Troubleshooting'],
                'cloud': ['Cloud_AWS', 'Cloud_Azure', 'DevOps_CI_CD', 'Kubernetes_Docker'],
                'windows': ['Windows_Server_2022', 'Windows_OS', 'Active_Directory', 
                           'Microsoft_365', 'SharePoint_Online'],
                'database': ['Database_SQL', 'ETL_Processes', 'Data_Warehousing']
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def load_data(self, file_path: str):
        """Load agents and tickets from JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.agents = {agent['agent_id']: agent for agent in data['agents']}
            self.tickets = {ticket['ticket_id']: ticket for ticket in data['tickets']}
            
            for agent_id in self.agents:
                self.agents[agent_id]['assigned_tickets'] = []
                self.agents[agent_id]['current_priority_load'] = 0
            
            logger.info(f"Loaded {len(self.agents)} agents and {len(self.tickets)} tickets")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise
    
    def extract_required_skills(self, ticket: Dict) -> Dict[str, float]:
        """
        Extract required skills from ticket description using NLP-like approach
        """
        if ticket['ticket_id'] in self.skill_requirements_cache:
            return self.skill_requirements_cache[ticket['ticket_id']]
        
        description = ticket['description'].lower()
        title = ticket['title'].lower()
        combined_text = f"{title} {description}"
        
        required_skills = {}
        
        skill_keywords = {
            'Networking': ['network', 'vpn', 'connection', 'connectivity', 'lan', 'wan'],
            'VPN_Troubleshooting': ['vpn', 'tunnel', 'remote', 'connection dropping'],
            'Linux_Administration': ['linux', 'ubuntu', 'debian', 'centos', 'bash', 'shell'],
            'Cloud_AWS': ['aws', 'amazon', 'ec2', 's3', 'lambda'],
            'Cloud_Azure': ['azure', 'microsoft cloud', 'app service'],
            'Hardware_Diagnostics': ['hardware', 'laptop', 'desktop', 'pc', 'computer', 'fan', 'battery'],
            'Windows_Server_2022': ['windows server', 'server 2022', 'windows 2022'],
            'Active_Directory': ['active directory', 'ad', 'domain', 'ldap', 'group policy'],
            'Microsoft_365': ['microsoft 365', 'm365', 'office 365', 'outlook', 'teams', 'sharepoint'],
            'Network_Security': ['firewall', 'security', 'breach', 'attack', 'vulnerability'],
            'Database_SQL': ['database', 'sql', 'query', 'mysql', 'postgresql', 'mssql'],
            'SharePoint_Online': ['sharepoint', 'document library', 'site collection'],
            'PowerShell_Scripting': ['powershell', 'ps1', 'script'],
            'Endpoint_Security': ['endpoint', 'antivirus', 'malware', 'edr'],
            'DevOps_CI_CD': ['devops', 'ci/cd', 'jenkins', 'pipeline', 'deployment'],
            'Kubernetes_Docker': ['kubernetes', 'k8s', 'docker', 'container', 'pod'],
            'Voice_VoIP': ['voip', 'phone', 'voice', 'telephony', 'sip'],
            'Printer_Troubleshooting': ['printer', 'print', 'printing'],
            'Mac_OS': ['mac', 'macos', 'osx', 'apple', 'macbook'],
            'SaaS_Integrations': ['saas', 'integration', 'api', 'webhook', 'sso', 'saml'],
            'Phishing_Analysis': ['phishing', 'spam', 'suspicious email', 'scam'],
            'SSL_Certificates': ['ssl', 'tls', 'certificate', 'https', 'encryption'],
            'DNS_Configuration': ['dns', 'domain', 'nameserver', 'resolution'],
            'Endpoint_Management': ['endpoint', 'mdm', 'intune', 'device management'],
            'Web_Server_Apache_Nginx': ['apache', 'nginx', 'web server', 'http'],
            'Firewall_Configuration': ['firewall', 'iptables', 'pf', 'acl', 'rules'],
            'Identity_Management': ['identity', 'iam', 'okta', 'auth0', 'authentication'],
            'Laptop_Repair': ['laptop', 'notebook', 'screen', 'keyboard', 'touchpad'],
            'Network_Cabling': ['cable', 'ethernet', 'cat5', 'cat6', 'rj45'],
            'Switch_Configuration': ['switch', 'vlan', 'trunk', 'spanning tree'],
            'Routing_Protocols': ['routing', 'ospf', 'bgp', 'eigrp', 'route'],
            'Cisco_IOS': ['cisco', 'ios', 'ccna', 'router', 'switch'],
            'Antivirus_Malware': ['antivirus', 'malware', 'virus', 'trojan', 'ransomware'],
            'Security_Audits': ['audit', 'compliance', 'assessment', 'vulnerability scan'],
            'SIEM_Logging': ['siem', 'log', 'splunk', 'elastic', 'monitoring'],
            'ETL_Processes': ['etl', 'extract', 'transform', 'load', 'data pipeline'],
            'Data_Warehousing': ['warehouse', 'data lake', 'bigquery', 'redshift'],
            'PowerBI_Tableau': ['powerbi', 'tableau', 'dashboard', 'visualization'],
            'API_Troubleshooting': ['api', 'rest', 'graphql', 'endpoint', 'integration'],
            'Software_Licensing': ['license', 'activation', 'subscription', 'seat'],
            'Virtualization_VMware': ['vmware', 'virtual', 'vm', 'esxi', 'vcenter'],
            'Python_Scripting': ['python', 'py', 'script', 'automation']
        }
        
        for skill, keywords in skill_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                required_skills[skill] = min(score / len(keywords), 1.0)
        
        self.skill_requirements_cache[ticket['ticket_id']] = required_skills
        
        return required_skills
    
    def calculate_ticket_priority(self, ticket: Dict) -> TicketPriority:
        """
        Calculate comprehensive ticket priority based on multiple factors
        """
        description = ticket['description'].lower()
        title = ticket['title'].lower()
        combined_text = f"{title} {description}"
        
        priority_score = 0
        
        critical_count = sum(1 for keyword in self.config['critical_keywords'] 
                           if keyword in combined_text)
        high_priority_count = sum(1 for keyword in self.config['high_priority_keywords']
                                if keyword in combined_text)
        
        business_impact = 0
        if 'production' in combined_text or 'business-critical' in combined_text:
            business_impact = 1.0
        elif 'public' in combined_text or 'customer' in combined_text:
            business_impact = 0.8
        elif 'internal' in combined_text or 'employee' in combined_text:
            business_impact = 0.5
        else:
            business_impact = 0.3
        
        affected_users = 1
        if 'all' in combined_text or 'everyone' in combined_text or 'company' in combined_text:
            affected_users = 100
        elif 'department' in combined_text or 'team' in combined_text or 'multiple' in combined_text:
            affected_users = 20
        elif 'group' in combined_text:
            affected_users = 10
        
        security_risk = 0
        security_keywords = ['breach', 'attack', 'phishing', 'malware', 'virus', 
                           'unauthorized', 'suspicious', 'security']
        security_count = sum(1 for keyword in security_keywords if keyword in combined_text)
        security_risk = min(security_count / len(security_keywords), 1.0)
        
        current_time = datetime.now().timestamp()
        age_hours = (current_time - ticket['creation_timestamp']) / 3600
        time_urgency = min(age_hours / 24, 1.0)
        
        priority_score = (
            critical_count * 10 +
            high_priority_count * 5 +
            business_impact * 8 +
            (affected_users / 10) +
            security_risk * 9 +
            time_urgency * 3
        )
        
        if priority_score >= 20:
            urgency_level = "CRITICAL"
        elif priority_score >= 15:
            urgency_level = "HIGH"
        elif priority_score >= 10:
            urgency_level = "MEDIUM"
        else:
            urgency_level = "LOW"
        
        return TicketPriority(
            ticket_id=ticket['ticket_id'],
            priority_score=priority_score,
            urgency_level=urgency_level,
            business_impact=business_impact,
            affected_users=affected_users,
            security_risk=security_risk
        )
    
    def calculate_agent_score(self, agent: Dict, ticket: Dict, 
                            ticket_priority: TicketPriority) -> float:
        """
        Calculate comprehensive agent suitability score for a ticket
        """
        required_skills = self.extract_required_skills(ticket)
        
        skill_match_score = 0
        matched_skills = 0
        for skill, importance in required_skills.items():
            if skill in agent['skills']:
                skill_match_score += agent['skills'][skill] * importance
                matched_skills += 1
        
        if required_skills:
            skill_match_score = skill_match_score / len(required_skills)
        else:
            skill_match_score = 5
        
        experience_score = min(agent['experience_level'] / 10, 1.0) * 10
        
        max_load = self.config['max_load_per_agent']
        workload_score = (1 - (agent['current_load'] / max_load)) * 10
        
        priority_capability = 0
        if ticket_priority.urgency_level == "CRITICAL" and agent['experience_level'] >= 8:
            priority_capability = 10
        elif ticket_priority.urgency_level == "HIGH" and agent['experience_level'] >= 6:
            priority_capability = 8
        elif ticket_priority.urgency_level == "MEDIUM" and agent['experience_level'] >= 4:
            priority_capability = 6
        else:
            priority_capability = 5
        
        performance_score = 5
        if agent['agent_id'] in self.agent_performance_history:
            history = self.agent_performance_history[agent['agent_id']]
            if history['total'] > 0:
                resolution_rate = history['resolved'] / history['total']
                performance_score = resolution_rate * 10
        
        final_score = (
            skill_match_score * self.config['skill_match_weight'] +
            experience_score * self.config['experience_weight'] +
            workload_score * self.config['workload_weight'] +
            priority_capability * self.config['priority_weight'] +
            performance_score * 0.1
        )
        
        if agent['availability_status'] != "Available":
            final_score *= 0.1
        
        if agent['current_load'] >= max_load:
            final_score *= 0.01
        
        return final_score
    
    def assign_tickets(self):
        """
        Main ticket assignment algorithm using priority queue and optimization
        """
        ticket_priorities = []
        for ticket_id, ticket in self.tickets.items():
            priority = self.calculate_ticket_priority(ticket)
            heapq.heappush(ticket_priorities, priority)
        
        while ticket_priorities:
            ticket_priority = heapq.heappop(ticket_priorities)
            ticket = self.tickets[ticket_priority.ticket_id]
            
            best_agent_id = None
            best_score = -1
            agent_scores = {}
            
            for agent_id, agent in self.agents.items():
                score = self.calculate_agent_score(agent, ticket, ticket_priority)
                agent_scores[agent_id] = score
                
                if score > best_score:
                    best_score = score
                    best_agent_id = agent_id
            
            if best_agent_id:
                agent = self.agents[best_agent_id]
                required_skills = self.extract_required_skills(ticket)
                
                rationale_parts = []
                
                matched_skills = [skill for skill in required_skills if skill in agent['skills']]
                if matched_skills:
                    skill_details = [f"{skill} ({agent['skills'].get(skill, 0)})" 
                                   for skill in matched_skills[:3]]
                    rationale_parts.append(f"Strong skills in {', '.join(skill_details)}")
                
                if agent['experience_level'] >= 10:
                    rationale_parts.append("senior expert level")
                elif agent['experience_level'] >= 7:
                    rationale_parts.append("experienced professional")
                elif agent['experience_level'] >= 4:
                    rationale_parts.append("competent handler")
                else:
                    rationale_parts.append("developing expertise")
                
                if agent['current_load'] <= 2:
                    rationale_parts.append("optimal workload capacity")
                elif agent['current_load'] <= 4:
                    rationale_parts.append("balanced workload")
                
                if ticket_priority.urgency_level in ["CRITICAL", "HIGH"]:
                    rationale_parts.append(f"capable of handling {ticket_priority.urgency_level} priority")
                
                rationale = f"Assigned to {agent['name']} ({agent_id}) - {', '.join(rationale_parts)}. " \
                          f"Match score: {best_score:.2f}, Priority: {ticket_priority.urgency_level}"
                
                assignment = {
                    'ticket_id': ticket['ticket_id'],
                    'title': ticket['title'],
                    'assigned_agent_id': best_agent_id,
                    'assigned_agent_name': agent['name'],
                    'priority': ticket_priority.urgency_level,
                    'priority_score': round(ticket_priority.priority_score, 2),
                    'business_impact': round(ticket_priority.business_impact, 2),
                    'affected_users': ticket_priority.affected_users,
                    'security_risk': round(ticket_priority.security_risk, 2),
                    'agent_match_score': round(best_score, 2),
                    'rationale': rationale,
                    'required_skills': list(required_skills.keys())[:5],
                    'agent_skills_matched': matched_skills[:5],
                    'timestamp': datetime.now().isoformat()
                }
                
                self.assignments.append(assignment)
                
                agent['current_load'] += 1
                agent['assigned_tickets'].append(ticket['ticket_id'])
                agent['current_priority_load'] += ticket_priority.priority_score
                
                logger.info(f"Assigned {ticket['ticket_id']} to {agent['name']} "
                          f"(Score: {best_score:.2f}, Priority: {ticket_priority.urgency_level})")
            else:
                logger.warning(f"Could not assign ticket {ticket['ticket_id']} - no suitable agent")
                
                self.assignments.append({
                    'ticket_id': ticket['ticket_id'],
                    'title': ticket['title'],
                    'assigned_agent_id': None,
                    'assigned_agent_name': "UNASSIGNED",
                    'priority': ticket_priority.urgency_level,
                    'priority_score': round(ticket_priority.priority_score, 2),
                    'rationale': "No suitable agent available - requires escalation or additional resources",
                    'timestamp': datetime.now().isoformat()
                })
    
    def generate_analytics(self) -> Dict:
        """Generate comprehensive analytics and insights"""
        analytics = {
            'summary': {
                'total_tickets': len(self.tickets),
                'total_agents': len(self.agents),
                'assigned_tickets': sum(1 for a in self.assignments if a['assigned_agent_id']),
                'unassigned_tickets': sum(1 for a in self.assignments if not a['assigned_agent_id'])
            },
            'priority_distribution': defaultdict(int),
            'agent_workload': {},
            'skill_demand': defaultdict(int),
            'skill_gaps': [],
            'recommendations': []
        }
        
        for assignment in self.assignments:
            analytics['priority_distribution'][assignment['priority']] += 1
        
        for agent_id, agent in self.agents.items():
            analytics['agent_workload'][agent['name']] = {
                'tickets_assigned': agent['current_load'],
                'priority_load': round(agent['current_priority_load'], 2),
                'utilization': f"{(agent['current_load'] / self.config['max_load_per_agent']) * 100:.1f}%"
            }
        
        for ticket in self.tickets.values():
            required_skills = self.extract_required_skills(ticket)
            for skill in required_skills:
                analytics['skill_demand'][skill] += 1
        
        top_demanded_skills = sorted(analytics['skill_demand'].items(), 
                                   key=lambda x: x[1], reverse=True)[:10]
        
        for skill, demand in top_demanded_skills:
            agents_with_skill = sum(1 for agent in self.agents.values() 
                                  if skill in agent['skills'] and agent['skills'][skill] >= 7)
            if agents_with_skill < 3:
                analytics['skill_gaps'].append({
                    'skill': skill,
                    'demand': demand,
                    'qualified_agents': agents_with_skill
                })
        
        if analytics['summary']['unassigned_tickets'] > 0:
            analytics['recommendations'].append(
                f"⚠️ {analytics['summary']['unassigned_tickets']} tickets remain unassigned - "
                "consider hiring or training additional agents"
            )
        
        if analytics['skill_gaps']:
            top_gap = analytics['skill_gaps'][0]
            analytics['recommendations'].append(
                f"🎯 Critical skill gap: {top_gap['skill']} - high demand ({top_gap['demand']} tickets) "
                f"but only {top_gap['qualified_agents']} qualified agents"
            )
        
        overloaded = [name for name, data in analytics['agent_workload'].items() 
                     if float(data['utilization'].rstrip('%')) > 80]
        if overloaded:
            analytics['recommendations'].append(
                f"⚡ {len(overloaded)} agents are over 80% capacity: {', '.join(overloaded[:3])}"
            )
        
        return analytics
    
    def save_results(self, output_path: str = 'output_result.json'):
        """Save assignment results and analytics"""
        output = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_tickets': len(self.tickets),
                'total_agents': len(self.agents),
                'assignments_made': len(self.assignments)
            },
            'assignments': self.assignments,
            'analytics': self.generate_analytics()
        }
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        logger.info(f"Results saved to {output_path}")
        
        simplified_output = {
            'assignments': [
                {
                    'ticket_id': a['ticket_id'],
                    'title': a['title'],
                    'assigned_agent_id': a['assigned_agent_id'],
                    'rationale': a['rationale']
                }
                for a in self.assignments[:10]
            ]
        }
        
        with open('output_result_simplified.json', 'w') as f:
            json.dump(simplified_output, f, indent=2)
    
    def run(self, input_file: str = 'dataset.json', output_file: str = 'output_result.json'):
        """Main execution method"""
        logger.info("Starting Intelligent Ticket Assignment System")
        
        self.load_data(input_file)
        
        logger.info("Beginning ticket assignment process...")
        self.assign_tickets()
        
        analytics = self.generate_analytics()
        
        self.save_results(output_file)
        
        print("\n" + "="*60)
        print("TICKET ASSIGNMENT COMPLETE")
        print("="*60)
        print(f"✅ Total Tickets Processed: {analytics['summary']['total_tickets']}")
        print(f"👥 Total Agents Available: {analytics['summary']['total_agents']}")
        print(f"📋 Successfully Assigned: {analytics['summary']['assigned_tickets']}")
        print(f"⚠️  Unassigned Tickets: {analytics['summary']['unassigned_tickets']}")
        print("\n📊 Priority Distribution:")
        for priority, count in analytics['priority_distribution'].items():
            print(f"   {priority}: {count} tickets")
        
        if analytics['recommendations']:
            print("\n💡 Key Recommendations:")
            for rec in analytics['recommendations']:
                print(f"   {rec}")
        
        print("\n📁 Full results saved to:", output_file)
        print("📁 Simplified results saved to: output_result_simplified.json")
        print("="*60)


def main():
    """Main entry point"""
    system = AdvancedTicketAssignmentSystem()
    system.run()


if __name__ == "__main__":
    main()
    