/*
  This sketch uses Timer1 in CTC mode with a computed OCR1A value to obtain an interrupt
  frequency as close as possible to a desired value (10.2 Hz in this example).

  In each Timer1 compare-match interrupt:
    - We compute the exact elapsed time.
    - We update a continuous sine wave value.
    - When 0.5 seconds or more have elapsed since the last sample, we update a sampled (BOZ) value.
    
  The main loop then prints these values.

  IMPORTANT: Avoid lengthy operations (like Serial printing) in the ISR.
  Here, the ISR only updates shared variables and sets flags, and the main loop performs the printing.
*/

#include <avr/io.h>
#include <avr/interrupt.h>
#include <math.h>



#define F_CPU 16000000UL  
#define DESIRED_FREQ 1 //doit etre <= 1 ou un exponent of 5 soit 5^x ou x entre 0 et 6 sinon il y a des incertitude sur le temps
#define PRESCALER 1024      
#define TIMER_TICKS (F_CPU / PRESCALER)
#define TIMER_TICKS_PER_SECOND (TIMER_TICKS / DESIRED_FREQ)
#define PWM_PIN 3
#define CONTROL_PIN 7

const uint16_t OCR1A_VALUE = (uint16_t)(TIMER_TICKS_PER_SECOND - 1);

volatile uint32_t gInterruptCount = 0;      
volatile bool newSampleFlag = false;    //flag pour dire qu'il y a une nouvelle valeur qui doit etre sampler
volatile float lastSampleTime = 0.0;    
volatile bool pulseTriggerFlag = false; // Set in the ISR when a pulse is requested

// Variables used for the extended pulse (handled in the main loop)
bool pulseActive = false;
unsigned long pulseStartTime = 0;
unsigned int extendedPulseDuration = 5; // Desired pulse duration in milliseconds

// Global Variables for ADC (3 channels)
//-------------------------------------------------
volatile uint16_t adcRawValue0 = 0; // ADC channel 0 (A0)
volatile uint16_t adcRawValue1 = 0; // ADC channel 1 (A1)
volatile uint16_t adcRawValue2 = 0; // ADC channel 2 (A2)
volatile uint8_t currentADCChannel = 0; // Tracks which channel was just read

// Sampled voltage values (updated every 0.5 s)
volatile float sampledVoltageA0 = 0.0;
volatile float sampledVoltageA1 = 0.0;
volatile float sampledVoltageA2 = 0.0;


ISR(TIMER1_COMPA_vect) {
        
    const float period = (float)(OCR1A_VALUE + 1) / (float)TIMER_TICKS;
    gInterruptCount++;  
    float currentTime = gInterruptCount * period; 
    
    // Zone de travail pour l'interrupt, faire code interrupt ici
    if ((currentTime - lastSampleTime) >= 0.5) {
        // Convert the raw ADC value (0–1023) to a voltage (assuming 5 V reference)
        sampledVoltageA0 = adcRawValue0 * (5.0 / 1023.0);
        sampledVoltageA1 = adcRawValue1 * (5.0 / 1023.0);
        sampledVoltageA2 = adcRawValue2 * (5.0 / 1023.0);
        newSampleFlag = true;
        lastSampleTime = currentTime;
    }
    pulseTriggerFlag = true;
}

ISR(ADC_vect) {
    uint16_t adcValue = ADC; // Read the 10-bit ADC result
    if (currentADCChannel == 0) {
        adcRawValue0 = adcValue;
        currentADCChannel = 1;
        ADMUX = (ADMUX & 0xF0) | 0x01; // Select ADC1 (A1)
    } else if (currentADCChannel == 1) {
        adcRawValue1 = adcValue;
        currentADCChannel = 2;
        ADMUX = (ADMUX & 0xF0) | 0x02; // Select ADC2 (A2)
    } else if (currentADCChannel == 2) {
        adcRawValue2 = adcValue;
        currentADCChannel = 0;
        ADMUX = (ADMUX & 0xF0) | 0x00; // Re-select ADC0 (A0)
    }
}

void ADC_Init() {
    ADMUX = (1 << REFS0);  // Use AVcc as the reference voltage, input on ADC0 (A0)
    // Enable ADC, its interrupt, auto-triggering (free-running mode), and set a prescaler.
    ADCSRA = (1 << ADEN) | (1 << ADIE) | (1 << ADATE) | (1 << ADPS2) | (1 << ADPS1); 
    ADCSRB = 0;           // Free-running mode
    DIDR0 = 0x1F;         // Disable digital input buffers on ADC0-ADC4 to reduce power consumption
}

void triggerExtendedPulse(unsigned int duration) {
    digitalWrite(CONTROL_PIN, HIGH);
    pulseActive = true;
    pulseStartTime = millis();
    extendedPulseDuration = duration;
}

void setup() {
    Serial.begin(9600);
    ADC_Init();  
    ADCSRA |= (1 << ADSC);

    pinMode(PWM_PIN, OUTPUT);

    pinMode(CONTROL_PIN, OUTPUT);
    digitalWrite(CONTROL_PIN, LOW);
  
  // --- Timer1 Setup ---
    cli();  // deactive les interrupt
    TCCR1A = 0;
    TCCR1B = 0;
    TCCR1B |= (1 << WGM12); // mode clear on compare match (reset le timer quand ca interrupt)
    OCR1A = OCR1A_VALUE; //compare register value
    TCCR1B |= (1 << CS12) | (1 << CS10); // prescaller of 1024
    TIMSK1 |= (1 << OCIE1A);  // Enable Timer1 compare-match interrupt
    sei(); //rearme les interrupt
}

void loop() {
    noInterrupts();
    bool sampleReady = newSampleFlag;
    float currSampleA0 = sampledVoltageA0;
    float currSampleA1 = sampledVoltageA1;
    float currSampleA2 = sampledVoltageA2;
    uint32_t interruptSnapshot = gInterruptCount;
    const float period = (float)(OCR1A_VALUE + 1) / (float)TIMER_TICKS;
    float currentTime = interruptSnapshot * period;
    if (sampleReady) newSampleFlag = false;
    interrupts();

    if (sampleReady) {
        Serial.print(currentTime * 1000, 1);  // Time in ms
        Serial.print(", ");
        Serial.print(currSampleA1, 3); 
        Serial.print(", ");
        Serial.print(currSampleA2, 3);
        Serial.print(", ");
        Serial.print(currSampleA0, 3);
        Serial.println("");


        float setpoint = 2.5;  // Desired voltage (V)
        float error = setpoint - currSampleA0;
        float Kp = 100.0;      // Proportional gain (adjust as needed)
        float baseDuty = 128;  // Base duty cycle (midpoint of 0–255)
        float control = baseDuty + (Kp * error);
        // Clamp control value to [0, 255]
        if (control > 255) control = 255;
        if (control < 0) control = 0;
        uint8_t pwmValue = (uint8_t) control;
        
        // Output the PWM signal on PWM_PIN
        analogWrite(PWM_PIN, pwmValue);
        
        //Serial.print("PWM Output: ");
        //Serial.println(pwmValue);
    }

    if (pulseTriggerFlag) {
        pulseTriggerFlag = false; // Clear the flag
        // Call the function to start the extended pulse with a desired duration (in ms)
        triggerExtendedPulse(5);  // For example, a 50 ms pulse
    }
    
    // If a pulse is active and the desired duration has elapsed, turn the pulse off.
    if (pulseActive && (millis() - pulseStartTime >= extendedPulseDuration)) {
        digitalWrite(CONTROL_PIN, LOW);
        pulseActive = false;
    }
}
