#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal.h>


#define RST_PIN 9
#define SS_PIN 10

byte readCard[4];
char* myTags[100] = {};
int tagsCount = 0;
String tagID = "";
boolean successRead = false;
boolean correctTag = false;


//Create Instances
MFRC522 mfrc522(SS_PIN, RST_PIN);
LiquidCrystal lcd(2, 3, 4, 5, 6, 7);



void setup() {
  // initiating
  SPI.begin();
  mfrc522.PCD_Init();
  lcd.begin(16, 2);

  lcd.print("-No Master Tag!-");
  lcd.setCursor(0, 1);
  lcd.print("SCAN NOW");

  while(!successRead) {
    successRead = getID();
    if (successRead == true) {
      myTags[tagsCount] = strdup(tagID.c_str());
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Master Tag Set!");

      tagsCount++;
    }
  }

  successRead = false;

  printNormalModeMessage();

}

uint8_t getID() {
  //Reads PICCs

  if (!mfrc522.PICC_IsNewCardPresent()) {
    return false;
  }

  if (!mfrc522.PICC_ReadCardSerial()) {
    return 0;
  }

  tagID = "";
  
  for (uint8_t i = 0; i < 4; i++) {
    readCard[i] = mfrc522.uid.uidByte[i];
    tagID.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
    tagID.toUpperCase();
    mfrc522.PICC_HaltA(); //stop reading
    return 1; 
}

void printNormalModeMessage() {
  delay(1500);
  lcd.clear();
  lcd.print("-Access Control-");
  lcd.setCursor(0, 1);
  lcd.print("Scan Your Tag");
}

void loop() {
  // put your main code here, to run repeatedly:

  //Scan a further tags
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return;
  }

  if (!mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  tagID = "";
  
  for (uint8_t i = 0; i < 4; i++) {
    readCard[i] = mfrc522.uid.uidByte[i];
    tagID.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
    tagID.toUpperCase();
    mfrc522.PICC_HaltA(); //stop reading

    correctTag = false;

    //Checks wether the scanned tag is the master tag
    if (tagID == myTags[0]) {
      lcd.clear();
      lcd.print("Program mode:");
      lcd.setCursor(0, 1);
      lcd.print("Add/Remove Tag");
      
      while (!successRead) {
        successRead = getID();
        
        if (successRead == true) {
          for (int i = 0; i < 100; i++) {
            if ( tagID == myTags[i]) {    //if tag is already saved in the array delete it!
              myTags[i] = "";
              lcd.clear();
              lcd.setCursor(0, 0);
              lcd.print(" Tag Removed!");
              printNormalModeMessage();
              return;
            }
          }
          myTags[tagsCount] = strdup(tagID.c_str());
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print(" Tag Added!");
          printNormalModeMessage();
          tagsCount++;
          return;
        }
      }
    }

    successRead = false;

    //checks whether the scanned tag is authorized
    for (int i = 0; i < 100; i++) {
      if (tagID == myTags[i]) {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Access Granted!");
        printNormalModeMessage();
        correctTag = true;
      }
    }

    if (correctTag == false) {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Access Denied!");
      printNormalModeMessage();
      
    }

}
