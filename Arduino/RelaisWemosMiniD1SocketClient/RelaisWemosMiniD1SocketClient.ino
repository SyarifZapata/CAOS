
#include <ESP8266WiFi.h>
#include <SocketIOClient.h>
#include <ArduinoJson.h>

StaticJsonBuffer<200> jsonBuffer;


SocketIOClient client;
const char* ssid     = "UPC9BC9117";
const char* password = "nHQ7s4hydznp";

char host[] = "139.162.182.153";
int port = 3008;

// Important otherwise it will disconnected
extern String RID;
extern String Rname;
extern String Rcontent;

unsigned long previous = 0;
unsigned long lastreply = 0;
unsigned long lastsend = 0;
String JSON;
JsonObject& root = jsonBuffer.createObject();

unsigned long previousMillis = 0;        // will store last temp was read
const long interval = 2000;

const int relayPin = D1;
int relayState = LOW;

void setup()   {                
  Serial.begin(9600);

  pinMode(relayPin, OUTPUT);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  if (!client.connect(host, port)) {
    Serial.println("connection failed");
    return;
  }
  
  if (client.connected()){
    client.send("connection", "message", "Connected !!!!");
  }
}


void loop() {
  if (client.connected()){
 
  unsigned long currentMillis = millis();
  if (currentMillis - previous > interval)
  {
    previous = currentMillis;
     client.heartbeat(0);
   
     lastsend = millis();
  }
    
  }else if (!client.connect(host, port)) {
     Serial.println("connection failed");
  }

  if (RID == "arduino" && Rname == "message"){
    Serial.println(Rcontent);
    if(Rcontent == "relayON"){
      digitalWrite(relayPin, HIGH);
      RID = "";
    }else if(Rcontent == "relayOFF"){
      digitalWrite(relayPin, LOW);
      RID = "";
    }
 
  }

  // let it to work

  if (client.monitor()){
    Serial.println(RID);
    if (RID == "atime" && Rname == "time"){
      Serial.print("Il est ");
      Serial.println(Rcontent);
    }
  }
}
