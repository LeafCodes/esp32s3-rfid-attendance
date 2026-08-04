#include "led_buzzer.h"
#include "config.h"

void Feedback::begin(byte buzzer, byte green, byte red) {
    buzzerPin = buzzer;
    greenPin = green;
    redPin = red;

    pinMode(buzzerPin, OUTPUT);
    pinMode(greenPin, OUTPUT);
    pinMode(redPin, OUTPUT);

    digitalWrite(buzzerPin, LOW);
    digitalWrite(greenPin, LOW);
    digitalWrite(redPin, LOW);

    Serial.println("Feedback: Buzzer=GPIO" + String(buzzer) + ", Green=GPIO" + String(green) + ", Red=GPIO" + String(red));
}

void Feedback::success() {
    digitalWrite(greenPin, HIGH);
    tone(buzzerPin, 2000, 200);
    delay(800);
    noTone(buzzerPin);
    digitalWrite(buzzerPin, LOW);
    digitalWrite(greenPin, LOW);
}

void Feedback::error() {
    digitalWrite(redPin, HIGH);
    for (int i = 0; i < 2; i++) {
        tone(buzzerPin, 800, 150);
        delay(150);
        noTone(buzzerPin);
        digitalWrite(buzzerPin, LOW);
        delay(100);
    }
    delay(500);
    digitalWrite(redPin, LOW);
}

void Feedback::warning() {
    for (int i = 0; i < 3; i++) {
        tone(buzzerPin, 1500, 80);
        delay(100);
        noTone(buzzerPin);
        digitalWrite(buzzerPin, LOW);
    }
}
