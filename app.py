from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json
import io
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

app = Flask(__name__)
CORS(app)

DATABASE = 'flood_data.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                 (id INTEGER PRIMARY KEY,
                  timestamp DATETIME,
                  water_height REAL,
                  rainfall REAL,
                  wind_speed REAL,
                  alert_status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alert_settings
                 (id INTEGER PRIMARY KEY,
                  water_height_threshold REAL,
                  rainfall_threshold REAL,
                  wind_speed_threshold REAL)''')

    c.execute('SELECT COUNT(*) FROM alert_settings')
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO alert_settings 
                     (water_height_threshold, rainfall_threshold, wind_speed_threshold)
                     VALUES (50, 100, 40)''')
    conn.commit()
    conn.close()

def get_alert_status(water_height, rainfall, wind_speed):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM alert_settings ORDER BY id DESC LIMIT 1')
    settings = c.fetchone()
    conn.close()
    
    if not settings:
        return "NORMAL"
    
    water_threshold, rainfall_threshold, wind_threshold = settings[1], settings[2], settings[3]
    
    # Determine alert level
    danger_count = 0
    if water_height > water_threshold:
        danger_count += 1
    if rainfall > rainfall_threshold:
        danger_count += 1
    if wind_speed > wind_threshold:
        danger_count += 1
    
    if danger_count >= 2:
        return "EMERGENCY"
    elif danger_count == 1 and (water_height > water_threshold * 0.8):
        return "WARNING"
    elif danger_count == 1:
        return "ALERT"
    else:
        return "NORMAL"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data/latest', methods=['GET'])
def get_latest_data():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 1')
    data = c.fetchone()
    conn.close()
    
    if data:
        return jsonify({
            'id': data[0],
            'timestamp': data[1],
            'water_height': data[2],
            'rainfall': data[3],
            'wind_speed': data[4],
            'alert_status': data[5]
        })
    else:
        return jsonify({'error': 'No data found'}), 404

@app.route('/api/data/history', methods=['GET'])
def get_history():
    limit = request.args.get('limit', 100, type=int)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT ?', (limit,))
    data = c.fetchall()
    conn.close()
    
    result = []
    for row in reversed(data):  # Reverse to get chronological order
        result.append({
            'id': row[0],
            'timestamp': row[1],
            'water_height': row[2],
            'rainfall': row[3],
            'wind_speed': row[4],
            'alert_status': row[5]
        })
    
    return jsonify(result)

@app.route('/api/data/add', methods=['POST'])
def add_sensor_data():
    try:
        data = request.get_json()
        water_height = float(data.get('water_height', 0))
        rainfall = float(data.get('rainfall', 0))
        wind_speed = float(data.get('wind_speed', 0))
        
        alert_status = get_alert_status(water_height, rainfall, wind_speed)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''INSERT INTO sensor_data 
                     (timestamp, water_height, rainfall, wind_speed, alert_status)
                     VALUES (?, ?, ?, ?, ?)''',
                  (timestamp, water_height, rainfall, wind_speed, alert_status))
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'alert_status': alert_status,
            'timestamp': timestamp
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/settings', methods=['GET'])
def get_settings():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM alert_settings ORDER BY id DESC LIMIT 1')
    settings = c.fetchone()
    conn.close()
    
    if settings:
        return jsonify({
            'water_height_threshold': settings[1],
            'rainfall_threshold': settings[2],
            'wind_speed_threshold': settings[3]
        })
    else:
        return jsonify({'error': 'No settings found'}), 404

@app.route('/api/settings/update', methods=['POST'])
def update_settings():
    try:
        data = request.get_json()
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''UPDATE alert_settings SET
                     water_height_threshold = ?,
                     rainfall_threshold = ?,
                     wind_speed_threshold = ?
                     WHERE id = (SELECT MAX(id) FROM alert_settings)''',
                  (data['water_height_threshold'], 
                   data['rainfall_threshold'],
                   data['wind_speed_threshold']))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC')
        data = c.fetchall()
        conn.close()

        wb = Workbook()
        ws = wb.active
        ws.title = "Sensor Data"

        headers = ['ID', 'Timestamp', 'Water Height (cm)', 'Rainfall (mm)', 'Wind Speed (km/h)', 'Alert Status']
        ws.append(headers)

        for row in reversed(data):
            ws.append(row)

        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 18
        ws.column_dimensions['D'].width = 16
        ws.column_dimensions['E'].width = 18
        ws.column_dimensions['F'].width = 15

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'flood_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/export/pdf', methods=['GET'])
def export_pdf():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 100')
        data = c.fetchall()
        c.execute('SELECT * FROM alert_settings ORDER BY id DESC LIMIT 1')
        settings = c.fetchone()
        conn.close()

        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#d32f2f'),
            spaceAfter=12,
            alignment=1
        )

        story.append(Paragraph('Laporan Data Sistem Peringatan Dini Banjir', title_style))
        story.append(Spacer(1, 0.2*inch))

        info_style = styles['Normal']
        story.append(Paragraph(f'<b>Tanggal Laporan:</b> {datetime.now().strftime("%d-%m-%Y %H:%M:%S")}', info_style))
        story.append(Spacer(1, 0.3*inch))

        if settings:
            story.append(Paragraph('<b>Pengaturan Ambang Batas:</b>', styles['Heading2']))
            threshold_data = [
                ['Parameter', 'Nilai'],
                ['Ketinggian Air', f'{settings[1]} cm'],
                ['Curah Hujan', f'{settings[2]} mm'],
                ['Kecepatan Angin', f'{settings[3]} km/h']
            ]
            threshold_table = Table(threshold_data, colWidths=[3*inch, 2*inch])
            threshold_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(threshold_table)
            story.append(Spacer(1, 0.3*inch))

        story.append(Paragraph('<b>Riwayat Data Sensor:</b>', styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        table_data = [['No', 'Waktu', 'Ket. Air (cm)', 'Hujan (mm)', 'Angin (km/h)', 'Status']]
        for idx, row in enumerate(reversed(data), 1):
            table_data.append([
                str(idx),
                row[1][:16],
                f'{row[2]:.1f}',
                f'{row[3]:.1f}',
                f'{row[4]:.1f}',
                row[5]
            ])
        
        data_table = Table(table_data, colWidths=[0.5*inch, 1.3*inch, 1.2*inch, 1.2*inch, 1.3*inch, 1.2*inch])
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(data_table)

        doc.build(story)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'banjir_gess_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        c.execute('SELECT AVG(water_height), MAX(water_height), MIN(water_height) FROM sensor_data')
        water_stats = c.fetchone()
        
        c.execute('SELECT AVG(rainfall), MAX(rainfall), MIN(rainfall) FROM sensor_data')
        rainfall_stats = c.fetchone()
        
        c.execute('SELECT AVG(wind_speed), MAX(wind_speed), MIN(wind_speed) FROM sensor_data')
        wind_stats = c.fetchone()
        
        c.execute('SELECT COUNT(*), SUM(CASE WHEN alert_status = "EMERGENCY" THEN 1 ELSE 0 END), SUM(CASE WHEN alert_status = "WARNING" THEN 1 ELSE 0 END) FROM sensor_data')
        alert_stats = c.fetchone()
        
        conn.close()
        
        return jsonify({
            'water_height': {
                'avg': water_stats[0],
                'max': water_stats[1],
                'min': water_stats[2]
            },
            'rainfall': {
                'avg': rainfall_stats[0],
                'max': rainfall_stats[1],
                'min': rainfall_stats[2]
            },
            'wind_speed': {
                'avg': wind_stats[0],
                'max': wind_stats[1],
                'min': wind_stats[2]
            },
            'total_records': alert_stats[0],
            'emergency_count': alert_stats[1],
            'warning_count': alert_stats[2]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
