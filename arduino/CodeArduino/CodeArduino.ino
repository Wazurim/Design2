#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <math.h>

#ifndef F_CPU
#define F_CPU 16000000UL
#endif

#define PWM_TOP 4095UL
#define PWM_PRESCALER 8UL 
#define ACTUAL_PWM_FREQ (F_CPU / (PWM_PRESCALER * (PWM_TOP + 1)))
#define DESIRED_ADC_UPDATE_FREQ 1.0
#define TIMER3_PRESCALER 1024UL
#define OCR3A_VALUE ((uint16_t)((F_CPU / (TIMER3_PRESCALER * DESIRED_ADC_UPDATE_FREQ)) - 1))


volatile uint32_t adcUpdateCount = 0;
volatile uint8_t currentChannel = 0;
volatile bool newSampleFlag = false;
volatile uint16_t adcRawValues[4];


// Control loop variables
bool running = false;
float Time = 0;
float CurrentTime = 0;
float consigne = 25; 

float P = 0.88;   
float I = 1/101.72;
float D = 0;
float F = 0;   
float previous_control = 0;
float previous_error = 0;
float previous_t2s[] = {25, 25, 25};
float previous_estimated_t3 = -1; 
bool isFirstPI = true;
int time_counter = 0;

const float dt = 1/DESIRED_ADC_UPDATE_FREQ; 


void handleLine(const String &line);
void parseParameters(const String &line);
float voltage_to_temp(float volt);

//
// Timer3 Compare Match A ISR
// Fires at the rate defined by DESIRED_ADC_UPDATE_FREQ (e.g., 1 Hz)
ISR(TIMER3_COMPA_vect) {

    adcUpdateCount++;
    currentChannel = 0; 
    ADMUX = (ADMUX & 0xF8) | currentChannel; 
    ADCSRA |= (1 << ADSC); 
}

//
// ADC Conversion Complete ISR
// The ADC is running in free-running mode and continuously updates the raw values.
ISR(ADC_vect) {
    adcRawValues[currentChannel] = ADC; 
    if (currentChannel < 3) {
        currentChannel++; // Move to the next channel
        ADMUX = (ADMUX & 0xF8) | currentChannel; // Set next ADC channel
        ADCSRA |= (1 << ADSC); // Start next conversion
    } else {
        newSampleFlag = true; 
    }
}

//
// ADC Initialization: uses AVcc as reference and enables ADC interrupts.
void ADC_Init() {
    ADMUX = (1 << REFS0);  // AVCC reference, start with channel 0
    ADCSRA = (1 << ADEN) | (1 << ADIE) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0); // Enable ADC, interrupt, prescaler = 128
    DIDR0 = 0x0F; // Disable digital input buffers on ADC0-ADC3
}

//
// Timer1 setup (PWM)
void setupTimer1(){
    TCCR1A = 0;
    TCCR1B = 0;
    TCCR1A |= (1 << COM1A1) | (1 << WGM11);
    TCCR1B |= (1 << WGM13) | (1 << WGM12);
    TCCR1B |= (1 << CS11);
    ICR1 = PWM_TOP;
    OCR1A = PWM_TOP / 2; 
}
//
// Timer3 setup (ADC)
void setupTimer3(){
    TCCR3A = 0;
    TCCR3B = 0;
    TCCR3B = (1 << WGM32) | (1 << CS32) | (1 << CS30); 
    OCR3A = OCR3A_VALUE; 
    TIMSK3 |= (1 << OCIE3A);  
}

//
// Setup function
void setup() {
    Serial.begin(115200);
    ADC_Init();
    ADCSRA |= (1 << ADSC);  
    pinMode(11, OUTPUT);

    cli(); // Disable interrupts during timer configuration
    setupTimer1();
    setupTimer3();
    sei(); // Re-enable interrupts

    Serial.println("Mega2560 started with split timers:");
    Serial.print("PWM Frequency (Timer1): ");
    Serial.print(ACTUAL_PWM_FREQ);
    Serial.println(" Hz (using full 16-bit resolution)");
    Serial.print("ADC Update Frequency (Timer3): ");
    Serial.print(DESIRED_ADC_UPDATE_FREQ);
    Serial.println(" Hz");
    Serial.println("Enter commands:");
    Serial.println("  p    -> start control loop");
    Serial.println("  S    -> stop control loop");
    Serial.println("  R    -> reset and new parameters");
    Serial.println("  PARAM C=2.5 F=1.0  -> set parameters (C = setpoint, F = frequency)");
}

//
// Main loop: When a new ADC sample is ready, update the PWM duty cycle based on control calculations.
void loop() {
    noInterrupts();
    bool sampleReady = newSampleFlag;
    float currSamplet2 = adcRawValues[0] * (5.0 / 1023.0);
    float currSamplet4 = adcRawValues[1] * (5.0 / 1023.0);
    float currSamplet1 = adcRawValues[2] * (5.0 / 1023.0);
    float currSamplet3 = adcRawValues[3] * (5.0 / 1023.0); 
    uint32_t updateCountSnapshot = adcUpdateCount;
    

    float pwmPeriod = (float)(PWM_TOP + 1) * ((float)PWM_PRESCALER / F_CPU);
    float trueTime = updateCountSnapshot / DESIRED_ADC_UPDATE_FREQ;
    CurrentTime = trueTime - Time;
    
    if (sampleReady) newSampleFlag = false;
    interrupts();
    
    if (Serial.available() > 0) {
        String line = Serial.readStringUntil('\n');
        line.trim();
        if (line.length() > 0) {
            handleLine(line);
        }
    }

    if (sampleReady) {
        if (previous_estimated_t3 < 0) {
            previous_estimated_t3 = voltage_to_tempt1(currSamplet2);
        }

        float estimated_tempt3 = (0.04431 * (previous_t2s[0]-25) + 0.9519 * (previous_estimated_t3-25))+25;
        previous_estimated_t3 = estimated_tempt3;
        previous_t2s[2] = previous_t2s[1];
        previous_t2s[1] = previous_t2s[0];
        previous_t2s[0] = voltage_to_tempt1(currSamplet2);

        if (running) {
            float error = (consigne - estimated_tempt3);
            const float dt = 1.0f / DESIRED_ADC_UPDATE_FREQ;
            float p = P;
            float i = I;
            float d = D;
            float f = F;
            float control = (previous_control + error * (i/2 + p) + previous_error * (i/2-p));

            if (control > 2.5f) {
                control = 2.5f;
            }
            else if (control < -2.5f) {
                control = -2.5f;
            }
            previous_control = control;
            // Adjust for operation point
            control += 2.5f;

            // Anti-windup
            if (control > 4.9f) {
                control = 4.9f;
            }
            else if (control < 0.1f) {
                control = 0.1f;
            }
            control = 5 - control;

            // Set previous values before going into PWM.
            previous_error = error;

            // Convert volts to PWM
            control = ((control-0.1f)/4.8f) * PWM_TOP;
            
            // Set PWM output
            uint16_t pwmValue = (uint16_t) control;
            OCR1A = pwmValue;

            Serial.print(trueTime * 1, 1); 
            Serial.print(" s | PWM : ");
            Serial.print(pwmValue);
            Serial.print(" / ");
            Serial.print(PWM_TOP);
            Serial.print(" | consigne: ");
            Serial.print(consigne, 3);
            Serial.print(" | t1: ");
            Serial.print(voltage_to_tempt1(currSamplet1), 3);
            Serial.print(" | t2: ");
            Serial.print(voltage_to_tempt1(currSamplet2), 3);
            Serial.print(" | t3: ");
            Serial.print(voltage_to_tempt3(currSamplet3), 3);
            Serial.print(" | t3 est: ");
            Serial.print(estimated_tempt3, 3);
            Serial.print(" | t4: ");
            Serial.print(voltage_to_tempt3(currSamplet4), 3);
            Serial.print(" | error: ");
            Serial.println(error, 3);

        else {
            OCR1A = PWM_TOP/2;
            Serial.print(trueTime * 1, 1);
            Serial.print(" s | PWM : ");
            Serial.print(PWM_TOP / 2);
            Serial.print(" / ");
            Serial.print(PWM_TOP);
            Serial.print(" | t1: ");
            Serial.print(voltage_to_tempt1(currSamplet1), 3);
            Serial.print(" | t2: ");
            Serial.print(voltage_to_tempt1(currSamplet2), 3);
            Serial.print(" | t3: ");
            Serial.print(voltage_to_tempt3(currSamplet3), 3);
            Serial.print(" | t3 est: ");
            Serial.print(estimated_tempt3, 3);
            Serial.print(" | t4: ");
            Serial.print(voltage_to_tempt3(currSamplet4), 3);
            Serial.println("\t Control OFF");
        }
    }
}

//
// Serial command processing functions
void handleLine(const String &line) {
    if (line.equalsIgnoreCase("p")) {
        running = true;
        Time = CurrentTime + Time;
        CurrentTime = 0;
        
        Serial.println("Control loop ON");
    } else if (line.equalsIgnoreCase("S")) {
        running = false;
        Serial.println("Control loop OFF");
    } else if (line.equalsIgnoreCase("R")) {
        running = false;
        previousControl = 0;
        Time = CurrentTime + Time;
        CurrentTime = 0;

    } else if (line.startsWith("PARAM")) {
        parseParameters(line);
    } else {
        Serial.print("Unknown command or format: ");
        Serial.println(line);
    }
}
void parseParameters(const String &line) {
    // Remove the command prefix (e.g., "PARAM ") 
    isFirstPI = true;
    int firstSpace = line.indexOf(' ');
    if(firstSpace == -1) {
        Serial.println("Invalid PARAM syntax. Use: PARAM C=... P=... I=... D=... F=...");
        return;
    }
    String params = line.substring(firstSpace + 1);
    int lastSpace = 0;
    while (true) {
        int nextSpace = params.indexOf(' ', lastSpace);
        String token;
        if (nextSpace == -1) {
            token = params.substring(lastSpace);
        } else {
            token = params.substring(lastSpace, nextSpace);
        }
        if (token.startsWith("C=")) {
            consigne = token.substring(2).toFloat();
        } else if (token.startsWith("P=")) {
            P = token.substring(2).toFloat();
            Serial.print("New P parameter received: ");
            Serial.println(P, 10);
        } else if (token.startsWith("I=")) {
            I = token.substring(2).toFloat();
            Serial.print("New I parameter received: ");
            Serial.println(I, 10);
        } else if (token.startsWith("D=")) {
            D = token.substring(2).toFloat();
            Serial.print("New D parameter received: ");
            Serial.println(D, 10);
        } else if (token.startsWith("F=")) {
            F = token.substring(2).toFloat();
            Serial.print("New F parameter received: ");
            Serial.println(F, 10);
        }
        if (nextSpace == -1) break;
        lastSpace = nextSpace + 1;
    }
    Serial.print("New setpoint (consigne) -> ");
    Serial.println(consigne);
}


// Function to convert voltage to temperature for T2 sensor
/// This function is used to convert the voltage reading from the T2 sensor to temperature in Celsius using Steinhart-Hart equation.
float voltage_to_tempt1(float volt) {
    const float A1 = 0.00335401643468053;
    const float B = 0.000256523550896126;
    const float C1 = 0.00000260597012072052;
    const float D1 = 0.000000063292612648746;
    const float RT = 10000.0;
    volt = volt * 0.32709f + 1.65306f;
    float res = 5 * (10000 - 2000 * volt) / volt;
    float logVal = log(RT / res);
    float temp = 1.0 / (A1 + B * logVal + C1 * logVal * logVal + D1 * logVal * logVal * logVal) - 273.15;
    return temp;
}

/// Function to convert voltage to temperature for T3 sensor
/// This function is used to convert the voltage reading from the T3 sensor to temperature in Celsius using Steinhart-Hart equation.
float voltage_to_tempt3(float volt) {
    const float A1 = 0.00335401643468053;
    const float B = 0.000256523550896126;
    const float C1 = 0.00000260597012072052;
    const float D1 = 0.000000063292612648746;
    const float RT = 10000.0;
    volt = volt * 0.1599f + 2.0406f;
    float res = 5 * (10000 - 2000 * volt) / volt;
    float logVal = log(RT / res);
    float temp = 1.0 / (A1 + B * logVal + C1 * logVal * logVal + D1 * logVal * logVal * logVal) - 273.15;
    return temp;
}

