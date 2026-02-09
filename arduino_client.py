import serial
import time
import requests
import json

ARDUINO_PORT = 'COM3' 
BAUD_RATE = 9600
API_URL = 'http://localhost:5000/api/data/add'

WATER_HEIGHT_CALIBRATION = 1.0  
RAINFALL_CALIBRATION = 2.0     
WIND_SPEED_CALIBRATION = 0.5   

def connect_arduino():
    try:
        ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Terhubung ke Arduino di {ARDUINO_PORT}")
        return ser
    except Exception as e:
        print(f"Error menghubung ke Arduino: {e}")
        return None

def read_sensor_data(ser):
    try:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            if line:
                values = line.split(',')
                if len(values) == 3:
                    water_height = float(values[0]) * WATER_HEIGHT_CALIBRATION
                    rainfall = float(values[1]) * RAINFALL_CALIBRATION
                    wind_speed = float(values[2]) * WIND_SPEED_CALIBRATION
                    
                    return {
                        'water_height': water_height,
                        'rainfall': rainfall,
                        'wind_speed': wind_speed
                    }
    except Exception as e:
        print(f"Error membaca data: {e}")
    
    return None

def send_to_api(data):
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Data berhasil dikirim - Status: {result['alert_status']}")
            return True
        else:
            print(f"Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error mengirim data: {e}")
        return False

def main():
    ser = connect_arduino()
    
    if ser is None:
        print("Gagal menghubung ke Arduino. Pastikan port dan kabel sudah benar.")
        return
    
    try:
        print("Memulai pengiriman data sensor...")
        while True:
            data = read_sensor_data(ser)
            if data:
                print(f"Sensor - Ketinggian: {data['water_height']:.1f} cm, "
                      f"Hujan: {data['rainfall']:.1f} mm, "
                      f"Angin: {data['wind_speed']:.1f} km/h")
                send_to_api(data)
            time.sleep(5)  
    except KeyboardInterrupt:
        print("\nMenghentikan program...")
    finally:
        ser.close()

if __name__ == '__main__':
    main()
