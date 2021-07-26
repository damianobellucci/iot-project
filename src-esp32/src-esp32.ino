/*****************************************/

#include <DHT.h>

#define DHTPIN 13
#define DHTTYPE DHT22

DHT dht(DHTPIN,DHTTYPE);
float temperature;
int counter;

void setup_temperature(){
  temperature = -300;
  counter = 0;
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

WiFiClient espClient;
PubSubClient client;

void setup_mqtt(){
  client.setClient(espClient);
  client.setServer(mqtt_server, mqtt_port);  
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
  client.loop();
  client.publish(in_topic, String(current_temperature()).c_str(), true);
  delay(3000);
}
