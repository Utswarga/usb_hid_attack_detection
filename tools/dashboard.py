"""
USB HID Attack Detection System - Web Dashboard

Provides real-time visualization of detection engine status,
test results, and system metrics through a web interface.
"""


import sys
from pathlib import Path

# Add parent directory to path so we can import core modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, jsonify, request
from datetime import datetime
from core.detection_engine import DetectionEngine, AttackSignal, AttackSeverity
from core.keystroke_analyzer import KeystrokeAnalyzer
from core.process_monitor import ProcessMonitor
from core.logger import StructuredLogger

logger = StructuredLogger(__name__)

# Initialize Flask app
app = Flask(
    __name__,
    template_folder=str(project_root / 'templates'),
    static_folder=str(project_root / 'templates')
)
app.config['JSON_SORT_KEYS'] = False

# Global state for dashboard APIs. This keeps demo state in-memory and avoids
# requiring a database for local monitoring/testing.
dashboard_state = {
    'detection_engine': DetectionEngine(),
    'keystroke_analyzer': KeystrokeAnalyzer(),
    'process_monitor': ProcessMonitor(),
    'system_status': 'idle',
    'start_time': datetime.now(),
}


@app.route('/')
def index():
    """Main dashboard page."""
    try:
        print("Rendering dashboard.html")
        with open(project_root / 'templates' / 'dashboard.html', 'r') as f:
            html = f.read()
        print(f"HTML length: {len(html)}")
        return html
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}", 500


@app.route('/api/system-status')
def get_system_status():
    """Get current system status."""
    engine = dashboard_state['detection_engine']
    monitor = dashboard_state['process_monitor']

    return jsonify({
        'status': dashboard_state['system_status'],
        'uptime': str(datetime.now() - dashboard_state['start_time']),
        'total_signals': len(engine.signal_history),
        'recent_signals': len(engine.get_recent_signals(minutes=0.1)),
        'baseline_processes': len(monitor._baseline_processes),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/signals')
def get_signals():
    """Get all recorded signals with optional filtering."""
    engine = dashboard_state['detection_engine']
    minutes = request.args.get('minutes', type=int, default=1)

    signals = engine.get_recent_signals(minutes=minutes)

    return jsonify({
        'total': len(signals),
        'signals': [
            {
                'type': s.signal_type,
                'severity': s.severity.name,
                'severity_value': s.severity.value,
                'timestamp': s.timestamp.isoformat(),
                'details': s.details
            }
            for s in signals
        ],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/statistics')
def get_statistics():
    """Get system statistics."""
    engine = dashboard_state['detection_engine']
    analyzer = dashboard_state['keystroke_analyzer']
    monitor = dashboard_state['process_monitor']

    # Calculate severity distribution
    severity_dist = {
        'LOW': 0,
        'MEDIUM': 0,
        'HIGH': 0,
        'CRITICAL': 0
    }

    for signal in engine.signal_history:
        severity_dist[signal.severity.name] += 1

    keystroke_stats = analyzer.get_statistics()

    return jsonify({
        'signals': {
            'total': len(engine.signal_history),
            'recent': len(engine.get_recent_signals(minutes=1)),
            'severity_distribution': severity_dist
        },
        'keystrokes': {
            'total_recorded': len(analyzer.keystroke_buffer),
            'average_wpm': keystroke_stats.get('average_wpm', 0),
            'max_wpm': keystroke_stats.get('max_wpm', 0),
            'abnormal_patterns': keystroke_stats.get('abnormal_patterns', 0)
        },
        'processes': {
            'baseline_count': len(monitor._baseline_processes),
            'total_tracked': len(monitor.process_history),
            'suspicious_recent': len([p for p in monitor.process_history if p.is_suspicious])
        }
    })


@app.route('/api/add-test-signal', methods=['POST'])
def add_test_signal():
    """Add a test signal to the engine."""
    data = request.json
    engine = dashboard_state['detection_engine']

    severity = AttackSeverity[data.get('severity', 'MEDIUM')]
    signal = AttackSignal(
        signal_type=data.get('type', 'test_signal'),
        severity=severity,
        details=data.get('details', {})
    )
    engine.add_signal(signal)

    return jsonify({
        'success': True,
        'message': f'Signal added: {signal.signal_type}',
        'signal': {
            'type': signal.signal_type,
            'severity': signal.severity.name,
            'timestamp': signal.timestamp.isoformat()
        }
    })


@app.route('/api/simulate-attack', methods=['POST'])
def simulate_attack():
    """Simulate an attack with multiple correlated signals."""
    engine = dashboard_state['detection_engine']

    # This sequence mirrors a common HID attack chain: USB insertion,
    # shell/process launch, then high-speed keystroke injection.
    attack_signals = [
        AttackSignal(
            signal_type='usb_insertion',
            severity=AttackSeverity.HIGH,
            details={'device': 'Unknown USB Device', 'product_id': '0x1234'}
        ),
        AttackSignal(
            signal_type='process_launch',
            severity=AttackSeverity.HIGH,
            details={'process': 'powershell.exe', 'pid': 9999}
        ),
        AttackSignal(
            signal_type='keystroke_burst',
            severity=AttackSeverity.MEDIUM,
            details={'wpm': 150, 'pattern_anomaly': True}
        ),
    ]

    for signal in attack_signals:
        engine.add_signal(signal)

    return jsonify({
        'success': True,
        'message': 'Attack simulation added (3 correlated signals)',
        'signals_added': len(attack_signals),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/clear-signals', methods=['POST'])
def clear_signals():
    """Clear all recorded signals."""
    engine = dashboard_state['detection_engine']
    engine.signal_history.clear()

    return jsonify({
        'success': True,
        'message': 'All signals cleared',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    })


def start_dashboard(host='127.0.0.1', port=5001, debug=False):
    """Start the Flask dashboard server."""
    logger.info(f"Starting dashboard on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    print("\n" + "="*80)
    print("USB HID ATTACK DETECTION - DASHBOARD SERVER")
    print("="*80)
    print("\n🌐 Dashboard available at: http://localhost:5001")
    print("\n📊 API endpoints:")
    print("   - GET  /api/system-status     → Current system status")
    print("   - GET  /api/signals           → All signals with filtering")
    print("   - GET  /api/statistics        → System statistics")
    print("   - POST /api/add-test-signal   → Add a test signal")
    print("   - POST /api/simulate-attack   → Simulate an attack")
    print("   - POST /api/clear-signals     → Clear all signals")
    print("   - GET  /api/health            → Health check")
    print("\n" + "="*80 + "\n")

    start_dashboard()
