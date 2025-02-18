#define NUM_CHANNELS 5
#define BUFFER_SIZE 100

#include <avr/io.h>
#include <avr/interrupt.h>

volatile uint16_t bufferA[NUM_CHANNELS][BUFFER_SIZE];
volatile uint16_t bufferB[NUM_CHANNELS][BUFFER_SIZE];
volatile uint16_t bufferC[NUM_CHANNELS][BUFFER_SIZE];

volatile uint8_t activeBuffer = 0;  // 0 = A, 1 = B, 2 = C
volatile uint8_t processingBuffer = 2;  // Buffer being processed in main loop
volatile uint8_t bufferReady = 0;   // Flag indicating a buffer is ready
volatile uint8_t currentChannel = 0;
volatile uint8_t bufferIndex = 0;
volatile uint8_t samplingEnabled = 0;  // Start/Stop sampling control

// ADC Initialization
void ADC_Init() {
    ADMUX = (1 << REFS0); // AVcc as reference
    ADCSRA = (1 << ADEN) | (1 << ADIE) | (1 << ADATE) | (1 << ADPS2) | (1 << ADPS1); 
    ADCSRB = 0; // Free running mode
    DIDR0 = 0x1F; // Disable digital input on ADC0-ADC4
}

// Timer1 Initialization for ADC Triggering
void Timer1_Init() {
    TCCR1A = 0;
    TCCR1B = (1 << WGM12) | (1 << CS11); // CTC mode, prescaler 8
    OCR1A = 19999; // 1 kHz sampling
    TIMSK1 = (1 << OCIE1A); 
}

// Timer1 Compare Match Interrupt (Triggers ADC)
ISR(TIMER1_COMPA_vect) {
    if (samplingEnabled) {
        ADMUX = (ADMUX & 0xF0) | (currentChannel & 0x0F); // Select ADC channel
        ADCSRA |= (1 << ADSC); // Start ADC conversion
    }
}

// ADC Conversion Complete Interrupt
ISR(ADC_vect) {
    uint16_t result = ADC;
    
    if (activeBuffer == 0) bufferA[currentChannel][bufferIndex] = result;
    else if (activeBuffer == 1) bufferB[currentChannel][bufferIndex] = result;
    else bufferC[currentChannel][bufferIndex] = result;

    currentChannel++;

    if (currentChannel >= NUM_CHANNELS) {
        currentChannel = 0;
        bufferIndex++;

        if (bufferIndex >= BUFFER_SIZE) {
            bufferIndex = 0;
            processingBuffer = activeBuffer;
            activeBuffer = (activeBuffer + 1) % 3; // Rotate buffers
            bufferReady = 1;
        }
    }
}

// UART Initialization
void UART_Init(unsigned int baud) {
    unsigned int ubrr = F_CPU / 16 / baud - 1;
    UBRR0H = (unsigned char)(ubrr >> 8);
    UBRR0L = (unsigned char)ubrr;
    UCSR0B = (1 << TXEN0) | (1 << RXEN0) | (1 << RXCIE0);
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
}

// UART Transmit Data
void UART_Transmit(uint16_t data) {
    while (!(UCSR0A & (1 << UDRE0)));
    UDR0 = (data >> 8);
    while (!(UCSR0A & (1 << UDRE0)));
    UDR0 = (data & 0xFF);
}

// UART Receive Interrupt for Commands
ISR(USART_RX_vect) {
    char command = UDR0;
    if (command == 'S') samplingEnabled = 1; // Start
    else if (command == 'P') samplingEnabled = 0; // Stop
}

void setup() {
    ADC_Init();
    Timer1_Init();
    UART_Init(9600);
    sei();
}
void loop(){
        if (bufferReady) {
            bufferReady = 0;
            volatile uint16_t (*readBuffer)[BUFFER_SIZE];

            if (processingBuffer == 0) readBuffer = bufferA;
            else if (processingBuffer == 1) readBuffer = bufferB;
            else readBuffer = bufferC;

            for (uint8_t ch = 0; ch < NUM_CHANNELS; ch++) {
                for (uint8_t i = 0; i < BUFFER_SIZE; i++) {
                  Serial.println(readBuffer[ch][i]);
                    UART_Transmit(readBuffer[ch][i]);
                }
            }
        }
    }

