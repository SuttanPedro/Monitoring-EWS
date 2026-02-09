const int WATER_HEIGHT_PIN = A0;   
const int RAINFALL_PIN = A1;       
const int WIND_SPEED_PIN = A2;    

void setup() {
  Serial.begin(9600);
  pinMode(WATER_HEIGHT_PIN, INPUT);
  pinMode(RAINFALL_PIN, INPUT);
  pinMode(WIND_SPEED_PIN, INPUT);
  
  delay(1000);
  Serial.println("Sistem Peringatan Dini Banjir - Arduino");
  Serial.println("======================================");
}

void loop() {
  int waterHeightRaw = analogRead(WATER_HEIGHT_PIN);
  int rainfallRaw = analogRead(RAINFALL_PIN);
  int windSpeedRaw = analogRead(WIND_SPEED_PIN);
  
  float waterHeight = (waterHeightRaw / 1023.0) * 100;
  float rainfall = (rainfallRaw / 1023.0) * 200;
  float windSpeed = (windSpeedRaw / 1023.0) * 100;
  
  Serial.print(waterHeight, 1);
  Serial.print(",");
  Serial.print(rainfall, 1);
  Serial.print(",");
  Serial.println(windSpeed, 1);
  
  delay(5000);
}
