/*****************************************/

#include <DHT.h>

#define DHTPIN 13
#define DHTTYPE DHT22

DHT dht(DHTPIN,DHTTYPE);
float temperature;
int counter;

void setup_temperature(){
  //temperature = -300;
  //counter = 0;
  dht.begin();
  Serial.begin(115200);
  dht.begin();
}

float current_temperature(){
  counter = counter + 1;
  Serial.print("Rilevazione temperatura n. : ");
  Serial.println(counter);
  float currentTemperature = dht.readTemperature();
  if ( temperature != currentTemperature ) {
    temperature = currentTemperature;
    Serial.print("Nuova temperatura: ");
    Serial.println(currentTemperature);
  }
  else {
      Serial.println("Temperatura: stabile");
  }
  return currentTemperature;
}

/****************************************/

#include <WiFi.h>

#define wifi_ssid "Bellucci"
#define wifi_password "casabelluccibiocco5865"

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(wifi_ssid);

  WiFi.begin(wifi_ssid, wifi_password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

/*****************************************/
#include <PubSubClient.h>

#define mqtt_server "130.136.2.70"
#define mqtt_port 1883
#define mqtt_user "IOTuser"
#define mqtt_password "IOTuser"
#define in_topic "temperature/damianobellucci"
#define topic_setting_parameters "settingparameters/damianobellucci"

WiFiClient espClient;
PubSubClient client;

int sample_frequency = NULL;
float min_temp, max_temp, min_moi, max_moi;

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  Serial.println();
  String string_setting_parameters;
  for (int i=0;i<length;i++) {
    //final_string[i]=(char)payload[i];
    string_setting_parameters.concat((char)payload[i]);
  }

  int ind1 = string_setting_parameters.indexOf(";");
  sample_frequency=string_setting_parameters.substring(0,ind1).toInt();

  int ind2 = string_setting_parameters.indexOf(";", ind1+1 );
  min_temp = string_setting_parameters.substring(ind1+1, ind2+1).toFloat(); 

  int ind3 = string_setting_parameters.indexOf(";", ind2+1 );
  max_temp = string_setting_parameters.substring(ind2+1, ind3+1).toFloat();

  int ind4 = string_setting_parameters.indexOf(";", ind3+1 );
  min_moi = string_setting_parameters.substring(ind3+1, ind4+1).toFloat();

  int ind5 = string_setting_parameters.indexOf(";", ind4+1 );
  max_moi = string_setting_parameters.substring(ind4+1, ind5+1).toFloat();

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

void setup_mqtt(){
  client.setClient(espClient);
  client.setServer(mqtt_server, mqtt_port);  
  client.setCallback(callback);
}

void reconnect_mqtt() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    // If you do not want to use a username and password, change next line to
    // if (client.connect("ESP8266Client")) {
    if (client.connect("ESPClient8798yh98", mqtt_user, mqtt_password)) {
      Serial.println("connected");
      client.subscribe(topic_setting_parameters,1);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

/*******************************************/

void setup() {
  Serial.begin(115200);
  setup_wifi();
  setup_mqtt();
  setup_temperature();
}

void loop() {
  if (!client.connected()) {
    reconnect_mqtt();
  }
  else{
    client.loop();
    if(sample_frequency!=NULL){ //controllo se è arrivato messaggio di retain
      client.publish(in_topic, String(current_temperature()).c_str());
      delay(sample_frequency);
    }
  }
}
