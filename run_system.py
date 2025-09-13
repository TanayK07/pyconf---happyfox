"""
run_system.py - Main execution script for the Intelligent Ticket Assignment System
"""

import sys
import argparse
import logging
from pathlib import Path
import json
from datetime import datetime

from ticket_assignment_system import AdvancedTicketAssignmentSystem
from ml_ticket_classifier import MLTicketClassifier
from dashboard import TicketDashboard, generate_dashboard
from utils import validate_data, ReportGenerator

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'ticket_system_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Intelligent Ticket Assignment System')
    parser.add_argument('--input', '-i', default='dataset.json', 
                       help='Input JSON file path')
    parser.add_argument('--output', '-o', default='output_result.json',
                       help='Output JSON file path')
    parser.add_argument('--config', '-c', default='config.json',
                       help='Configuration file path')
    parser.add_argument('--ml-enhanced', action='store_true',
                       help='Enable ML-enhanced classification')
    parser.add_argument('--dashboard', action='store_true',
                       help='Generate dashboard after assignment')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--validate-only', action='store_true',
                       help='Only validate input data')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    print("="*60)
    print("INTELLIGENT TICKET ASSIGNMENT SYSTEM")
    print("PyCon25 Hackathon Project")
    print("="*60)
    print()
    
    print(" Validating input data...")
    is_valid, errors = validate_data(args.input)
    
    if not is_valid:
        print(" Validation failed:")
        for error in errors:
            print(f"   - {error}")
        sys.exit(1)
    
    print(" Input data validated successfully")
    
    if args.validate_only:
        print("Validation complete. Exiting...")
        sys.exit(0)
    
    print("\n Initializing assignment system...")
    system = AdvancedTicketAssignmentSystem(args.config)
    
    print(" Loading data...")
    system.load_data(args.input)
    
    if args.ml_enhanced:
        print("\n Enabling ML-enhanced classification...")
        ml_classifier = MLTicketClassifier()
        
        with open(args.input, 'r') as f:
            data = json.load(f)
        
        ml_classifier.train_skill_model(data['tickets'], data['agents'])
        print(" ML model trained")
        
        ml_classifier.save_model('ml_model.pkl')
        print(" ML model saved")
    
    print("\n Starting ticket assignment process...")
    system.assign_tickets()
    
    print("\n Saving results...")
    system.save_results(args.output)
    
    analytics = system.generate_analytics()
    
    print("\n" + "="*60)
    print("ASSIGNMENT COMPLETE - SUMMARY")
    print("="*60)
    print(f" Total Tickets: {analytics['summary']['total_tickets']}")
    print(f" Assigned: {analytics['summary']['assigned_tickets']}")
    print(f"  Unassigned: {analytics['summary']['unassigned_tickets']}")
    
    success_rate = (analytics['summary']['assigned_tickets'] / 
                   analytics['summary']['total_tickets'] * 100)
    print(f" Success Rate: {success_rate:.1f}%")
    
    print("\n Priority Distribution:")
    for priority, count in sorted(analytics['priority_distribution'].items()):
        print(f"   {priority}: {count}")
    
    if analytics['skill_gaps']:
        print("\n Critical Skill Gaps:")
        for gap in analytics['skill_gaps'][:3]:
            print(f"   - {gap['skill']}: {gap['demand']} tickets, {gap['qualified_agents']} agents")
    
    if analytics['recommendations']:
        print("\n💡 Recommendations:")
        for rec in analytics['recommendations'][:3]:
            print(f"   • {rec}")
    
    if args.dashboard:
        print("\n Generating dashboard...")
        dashboard = TicketDashboard()
        
        with open(args.output, 'r') as f:
            output_data = json.load(f)
        
        dashboard.update_metrics(output_data['assignments'])
        dashboard.generate_visualizations()
        dashboard.generate_report()
        print(" Dashboard generated in 'dashboard_output' directory")
    
    print("\n" + "="*60)
    print(" SYSTEM EXECUTION COMPLETE")
    print(f" Results saved to: {args.output}")
    print(f" Simplified results: output_result_simplified.json")
    if args.dashboard:
        print(" Dashboard: dashboard_output/")
    print("="*60)

if __name__ == "__main__":
    main()