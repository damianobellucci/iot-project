/**********SOIL MOISTURE SENSOR************************/
int readSoilMoisture(){
    const int dry = 2865;
    const int wet = 1164;
    int pin_soil_moisture = 34;
    int sensorValue = analogRead(pin_soil_moisture);
    int value = map(sensorValue,wet,dry,100,0);
    if(value>100)return 100;
    else if(value<0)return 0;
    return(value);
}

/*********TEMPERATURE/HUMIDITY SENSOR*******************/

#include <DHT.h>
#define DHTPIN 13
#define DHTTYPE DHT22
DHT dht(DHTPIN,DHTTYPE);

/*******************WIFI***********************************/
#include <WiFi.h>

const char ssid[] = "Bellucci";
const char pass[] = "casabelluccibiocco5865";
WiFiClient net;

void wifiConnect() {
  Serial.print("checking wifi...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nconnected!");
}
/******************************************************/

/*****************MQTT*********************************/
#include <MQTT.h>
MQTTClient client;

#define mqtt_server "130.136.2.70"
#define mqtt_port 1883
#define mqtt_user "IOTuser"
#define mqtt_password "IOTuser"
#define in_topic "damianobellucci/test"
#define topic_setting_parameters "damianobellucci/test_setting_parameters"

void mqttConnect(){
  //bool connect(const char clientID[], const char username[], const char password[], bool skip = false);
  while (!client.connect("arduino", mqtt_user, mqtt_password)) {
    Serial.print(".");
    delay(1000);
  }
  
  Serial.println("\n mqtt connected!");

  client.subscribe(topic_setting_parameters, 2);
}


int sample_frequency = NULL;
float min_temp, max_temp, min_moi, max_moi;

void messageReceived(String &topic, String &payload) {
  Serial.println("incoming: " + topic + " - " + payload);

  int ind1 = payload.indexOf(";");
  sample_frequency=payload.substring(0,ind1).toInt();

  int ind2 = payload.indexOf(";", ind1+1 );
  min_temp = payload.substring(ind1+1, ind2+1).toFloat(); 

  int ind3 = payload.indexOf(";", ind2+1 );
  max_temp = payload.substring(ind2+1, ind3+1).toFloat();

  int ind4 = payload.indexOf(";", ind3+1 );
  min_moi = payload.substring(ind3+1, ind4+1).toFloat();

  int ind5 = payload.indexOf(";", ind4+1 );
  max_moi = payload.substring(ind4+1, ind5+1).toFloat();

  Serial.println("Sample frequency:");
  Serial.println(sample_frequency);

  Serial.println("min temp:");
  Serial.println(min_temp);

  Serial.println("max temp:");
  Serial.println(max_temp);

  Serial.println("min_moi:");
  Serial.println(min_moi);

  Serial.println("max_moi:");
  Serial.println(max_moi);


}

/********************************************************/
#define ID_THIS_ESP32 "1520"
#define GPS_COORDINATES "41.890209,12.492231"
#define ONBOARD_LED 2

void setup() {
  Serial.begin(115200);
  
  dht.begin();
  
  WiFi.begin(ssid, pass);

  client.begin(mqtt_server,mqtt_port, net);
  client.onMessage(messageReceived);
  client.subscribe(topic_setting_parameters, 2);
  
  wifiConnect();

  pinMode(ONBOARD_LED,OUTPUT);
}

void loop(){
 
  //wifi
  if(WiFi.status() != WL_CONNECTED){
    wifiConnect();
  }

  //mqtt
  client.loop();
  if(!client.connected()){
    mqttConnect();
  }
  

  //collecting sensor data
  if(sample_frequency!=NULL){
    
    int soil_moisture = readSoilMoisture();
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    String payload_string;
    String comma=";";
     
    payload_string.concat(String(temperature));
    payload_string.concat(comma);
    payload_string.concat(String(humidity));
    payload_string.concat(comma);
    payload_string.concat(String(ID_THIS_ESP32));
    payload_string.concat(comma);
    payload_string.concat(String(GPS_COORDINATES));
    payload_string.concat(comma);
    payload_string.concat(String(WiFi.RSSI()));
    payload_string.concat(comma);
    payload_string.concat(soil_moisture);
    payload_string.concat(comma);
    
    char payload[payload_string.length()+1];
    payload_string.toCharArray(payload, payload_string.length()+1);
    Serial.println(payload);
    
    client.publish(in_topic,payload ,strlen(payload), false, 2);

    if(temperature<min_temp || temperature>max_temp){
      digitalWrite(ONBOARD_LED,HIGH);
      delay(100);
      digitalWrite(ONBOARD_LED,LOW);
    }
    delay(sample_frequency);    
  }
  }
