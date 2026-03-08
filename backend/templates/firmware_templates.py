from __future__ import annotations

MCU_ALIASES = {
    "lpc2148": "LPC2148",
    "arduino": "Arduino Uno",
    "arduino uno": "Arduino Uno",
    "esp32": "ESP32",
    "pic16f877a": "PIC16F877A",
}

SUPPORTED_MCUS = tuple(MCU_ALIASES.values())
SUPPORTED_PERIPHERALS = ("uart", "adc", "pwm", "gpio", "spi", "i2c", "timers")


def normalize_mcu(microcontroller: str) -> str:
    key = microcontroller.strip().lower()
    return MCU_ALIASES.get(key, microcontroller)


def detect_peripheral(task: str) -> str | None:
    lowered = task.lower()
    for peripheral in SUPPORTED_PERIPHERALS:
        if peripheral in lowered:
            return peripheral
    if "timer" in lowered:
        return "timers"
    return None


def get_template(mcu: str, peripheral: str) -> str:
    return TEMPLATE_LIBRARY[mcu][peripheral]


def get_pin_configuration(mcu: str, peripheral: str) -> list[dict[str, str]]:
    return PIN_CONFIGURATION[mcu][peripheral]


TEMPLATE_LIBRARY: dict[str, dict[str, str]] = {
    "LPC2148": {
        "uart": """// LPC2148 UART0 initialization and polling example\n#include <LPC214x.h>\n\nvoid uart0_init(void) {\n    PINSEL0 |= (1U << 0) | (1U << 2);      // P0.0=TXD0, P0.1=RXD0\n    U0LCR = 0x83;                          // 8-bit, 1 stop, no parity, DLAB=1\n    U0DLL = 97;                            // 15MHz PCLK -> 9600 baud\n    U0DLM = 0;\n    U0LCR = 0x03;                          // DLAB=0\n}\n\nvoid uart0_putc(char c) {\n    while ((U0LSR & (1U << 5)) == 0U) { }  // THR empty\n    U0THR = c;\n}\n\nint main(void) {\n    uart0_init();\n    while (1) {\n        uart0_putc('U');\n        for (volatile unsigned i = 0; i < 500000; ++i) { }\n    }\n}\n""",
        "adc": """// LPC2148 ADC0.1 sampling example\n#include <LPC214x.h>\n\nvoid adc_init(void) {\n    PINSEL1 |= (1U << 24);                 // P0.28 -> AD0.1\n    AD0CR = (1U << 1) | (4U << 8) | (1U << 21);  // SEL=CH1, CLKDIV=4, ADC enable\n}\n\nunsigned short adc_read_ch1(void) {\n    AD0CR |= (1U << 24);                   // Start conversion now\n    while ((AD0DR1 & (1U << 31)) == 0U) { }\n    return (unsigned short)((AD0DR1 >> 6) & 0x3FFU);\n}\n\nint main(void) {\n    adc_init();\n    while (1) {\n        volatile unsigned short sample = adc_read_ch1();\n        (void)sample;\n    }\n}\n""",
        "pwm": """// LPC2148 PWM1 setup on P0.0\n#include <LPC214x.h>\n\nvoid pwm1_init(void) {\n    PINSEL0 |= (1U << 0);                  // P0.0 -> PWM1\n    PWMPR = 14;                            // 1 MHz PWM clock from 15MHz PCLK\n    PWMMR0 = 1000;                         // 1 kHz period\n    PWMMR1 = 500;                          // 50% duty\n    PWMMCR = (1U << 1);                    // Reset on MR0\n    PWMLER = (1U << 0) | (1U << 1);\n    PWMPCR = (1U << 9);                    // Enable PWM1 output\n    PWMTCR = (1U << 0) | (1U << 3);        // Counter + PWM enable\n}\n\nint main(void) {\n    pwm1_init();\n    while (1) { }\n}\n""",
        "gpio": """// LPC2148 GPIO blink on P0.10\n#include <LPC214x.h>\n\nvoid gpio_init(void) {\n    IODIR0 |= (1U << 10);                  // P0.10 output\n}\n\nvoid delay(void) {\n    for (volatile unsigned i = 0; i < 400000; ++i) { }\n}\n\nint main(void) {\n    gpio_init();\n    while (1) {\n        IOSET0 = (1U << 10);\n        delay();\n        IOCLR0 = (1U << 10);\n        delay();\n    }\n}\n""",
        "spi": """// LPC2148 SPI0 transfer example\n#include <LPC214x.h>\n\nvoid spi0_init(void) {\n    PINSEL0 |= (1U << 8) | (1U << 10) | (1U << 12); // SCK0,MISO0,MOSI0\n    S0SPCCR = 8;                             // SPI clock divider\n    S0SPCR = (1U << 5) | (1U << 3);          // Master mode, CPOL=1\n}\n\nunsigned char spi0_transfer(unsigned char data) {\n    S0SPDR = data;\n    while ((S0SPSR & (1U << 7)) == 0U) { }   // SPIF\n    return (unsigned char)S0SPDR;\n}\n\nint main(void) {\n    spi0_init();\n    while (1) {\n        volatile unsigned char rx = spi0_transfer(0x55);\n        (void)rx;\n    }\n}\n""",
        "i2c": """// LPC2148 I2C0 initialization and start condition\n#include <LPC214x.h>\n\nvoid i2c0_init(void) {\n    PINSEL0 |= (1U << 4) | (1U << 6);      // P0.2=SCL0, P0.3=SDA0\n    I2C0SCLH = 75;\n    I2C0SCLL = 75;                          // ~100 kHz\n    I2C0CONSET = (1U << 6);                 // I2EN\n}\n\nvoid i2c0_start(void) {\n    I2C0CONSET = (1U << 5);                 // STA\n    while ((I2C0CONSET & (1U << 3)) == 0U) { }\n}\n\nint main(void) {\n    i2c0_init();\n    while (1) {\n        i2c0_start();\n        I2C0CONCLR = (1U << 5);\n    }\n}\n""",
        "timers": """// LPC2148 Timer0 periodic tick\n#include <LPC214x.h>\n\nvoid timer0_init(void) {\n    T0PR = 14999;                           // 1 ms tick at 15MHz\n    T0MR0 = 1000;                           // 1 second\n    T0MCR = (1U << 0) | (1U << 1);          // Interrupt + reset on MR0\n    T0TCR = 1;                              // Enable timer\n}\n\nint main(void) {\n    timer0_init();\n    while (1) {\n        if (T0IR & 1U) {\n            T0IR = 1U;\n            // 1-second task hook\n        }\n    }\n}\n""",
    },
    "Arduino Uno": {
        "uart": """// Arduino Uno UART using AVR registers\n#include <avr/io.h>\n\nvoid uart_init(void) {\n    unsigned int ubrr = 103;                // 9600 @ 16MHz\n    UBRR0H = (unsigned char)(ubrr >> 8);\n    UBRR0L = (unsigned char)ubrr;\n    UCSR0B = (1U << TXEN0) | (1U << RXEN0);\n    UCSR0C = (1U << UCSZ01) | (1U << UCSZ00); // 8N1\n}\n\nvoid uart_putc(char c) {\n    while (!(UCSR0A & (1U << UDRE0))) { }\n    UDR0 = c;\n}\n\nint main(void) {\n    uart_init();\n    while (1) { uart_putc('A'); }\n}\n""",
        "adc": """// Arduino Uno ADC channel 0\n#include <avr/io.h>\n\nvoid adc_init(void) {\n    ADMUX = (1U << REFS0);                  // AVcc reference, ADC0\n    ADCSRA = (1U << ADEN) | (1U << ADPS2) | (1U << ADPS1); // enable, /64\n}\n\nunsigned short adc_read(void) {\n    ADCSRA |= (1U << ADSC);\n    while (ADCSRA & (1U << ADSC)) { }\n    return ADC;\n}\n\nint main(void) {\n    adc_init();\n    while (1) { volatile unsigned short v = adc_read(); (void)v; }\n}\n""",
        "pwm": """// Arduino Uno PWM on OC1A (D9)\n#include <avr/io.h>\n\nvoid pwm_init(void) {\n    DDRB |= (1U << PB1);                    // D9 output\n    TCCR1A = (1U << COM1A1) | (1U << WGM11);\n    TCCR1B = (1U << WGM13) | (1U << WGM12) | (1U << CS11); // prescaler 8\n    ICR1 = 19999;                           // 50Hz\n    OCR1A = 1500;                           // neutral pulse\n}\n\nint main(void) {\n    pwm_init();\n    while (1) { }\n}\n""",
        "gpio": """// Arduino Uno GPIO blink on PB5 (D13)\n#include <avr/io.h>\n\nvoid gpio_init(void) {\n    DDRB |= (1U << PB5);\n}\n\nvoid delay(void) {\n    for (volatile unsigned long i = 0; i < 200000UL; ++i) { }\n}\n\nint main(void) {\n    gpio_init();\n    while (1) {\n        PORTB ^= (1U << PB5);\n        delay();\n    }\n}\n""",
        "spi": """// Arduino Uno SPI master mode\n#include <avr/io.h>\n\nvoid spi_init(void) {\n    DDRB |= (1U << PB3) | (1U << PB5) | (1U << PB2); // MOSI,SCK,SS outputs\n    DDRB &= ~(1U << PB4);\n    SPCR = (1U << SPE) | (1U << MSTR) | (1U << SPR0);\n}\n\nunsigned char spi_transfer(unsigned char data) {\n    SPDR = data;\n    while (!(SPSR & (1U << SPIF))) { }\n    return SPDR;\n}\n\nint main(void) {\n    spi_init();\n    while (1) { volatile unsigned char x = spi_transfer(0x9A); (void)x; }\n}\n""",
        "i2c": """// Arduino Uno TWI (I2C) at 100kHz\n#include <avr/io.h>\n\nvoid i2c_init(void) {\n    TWSR = 0x00;\n    TWBR = 72;                              // ~100kHz at 16MHz\n    TWCR = (1U << TWEN);\n}\n\nvoid i2c_start(void) {\n    TWCR = (1U << TWINT) | (1U << TWSTA) | (1U << TWEN);\n    while (!(TWCR & (1U << TWINT))) { }\n}\n\nint main(void) {\n    i2c_init();\n    while (1) { i2c_start(); }\n}\n""",
        "timers": """// Arduino Uno Timer0 compare match polling\n#include <avr/io.h>\n\nvoid timer0_init(void) {\n    TCCR0A = (1U << WGM01);                 // CTC mode\n    TCCR0B = (1U << CS02) | (1U << CS00);   // prescaler 1024\n    OCR0A = 156;                            // ~10ms tick\n}\n\nint main(void) {\n    timer0_init();\n    while (1) {\n        if (TIFR0 & (1U << OCF0A)) {\n            TIFR0 = (1U << OCF0A);\n            // periodic task\n        }\n    }\n}\n""",
    },
    "ESP32": {
        "uart": """// ESP32 UART2 example (ESP-IDF style registers hidden by driver)\n#include "driver/uart.h"\n\nvoid uart_init(void) {\n    uart_config_t cfg = {\n        .baud_rate = 115200, .data_bits = UART_DATA_8_BITS,\n        .parity = UART_PARITY_DISABLE, .stop_bits = UART_STOP_BITS_1,\n        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE\n    };\n    uart_param_config(UART_NUM_2, &cfg);\n    uart_set_pin(UART_NUM_2, 17, 16, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);\n    uart_driver_install(UART_NUM_2, 1024, 0, 0, NULL, 0);\n}\n\nvoid app_main(void) {\n    uart_init();\n    while (1) { uart_write_bytes(UART_NUM_2, "ESP32\\n", 6); vTaskDelay(pdMS_TO_TICKS(1000)); }\n}\n""",
        "adc": """// ESP32 ADC1 channel read\n#include "driver/adc.h"\n#include "esp_adc_cal.h"\n\nvoid adc_init(void) {\n    adc1_config_width(ADC_WIDTH_BIT_12);\n    adc1_config_channel_atten(ADC1_CHANNEL_6, ADC_ATTEN_DB_11); // GPIO34\n}\n\nvoid app_main(void) {\n    adc_init();\n    while (1) {\n        int raw = adc1_get_raw(ADC1_CHANNEL_6);\n        (void)raw;\n        vTaskDelay(pdMS_TO_TICKS(1000));\n    }\n}\n""",
        "pwm": """// ESP32 LEDC PWM on GPIO18\n#include "driver/ledc.h"\n\nvoid pwm_init(void) {\n    ledc_timer_config_t timer = {.speed_mode = LEDC_HIGH_SPEED_MODE, .timer_num = LEDC_TIMER_0, .duty_resolution = LEDC_TIMER_10_BIT, .freq_hz = 1000};\n    ledc_channel_config_t channel = {.gpio_num = 18, .speed_mode = LEDC_HIGH_SPEED_MODE, .channel = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0, .duty = 512};\n    ledc_timer_config(&timer);\n    ledc_channel_config(&channel);\n}\n\nvoid app_main(void) {\n    pwm_init();\n    while (1) { }\n}\n""",
        "gpio": """// ESP32 GPIO output toggle\n#include "driver/gpio.h"\n\nvoid gpio_init(void) {\n    gpio_config_t io = {.pin_bit_mask = (1ULL << 2), .mode = GPIO_MODE_OUTPUT};\n    gpio_config(&io);\n}\n\nvoid app_main(void) {\n    gpio_init();\n    while (1) {\n        gpio_set_level(GPIO_NUM_2, 1);\n        vTaskDelay(pdMS_TO_TICKS(500));\n        gpio_set_level(GPIO_NUM_2, 0);\n        vTaskDelay(pdMS_TO_TICKS(500));\n    }\n}\n""",
        "spi": """// ESP32 SPI master using VSPI\n#include "driver/spi_master.h"\n\nstatic spi_device_handle_t spi;\n\nvoid spi_init(void) {\n    spi_bus_config_t bus = {.mosi_io_num = 23, .miso_io_num = 19, .sclk_io_num = 18};\n    spi_device_interface_config_t dev = {.clock_speed_hz = 1 * 1000 * 1000, .mode = 0, .spics_io_num = 5, .queue_size = 1};\n    spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO);\n    spi_bus_add_device(SPI2_HOST, &dev, &spi);\n}\n\nvoid app_main(void) {\n    spi_init();\n    while (1) { spi_transaction_t t = {.length = 8, .tx_buffer = "\\xA5"}; spi_device_transmit(spi, &t); }\n}\n""",
        "i2c": """// ESP32 I2C master initialization\n#include "driver/i2c.h"\n\nvoid i2c_init(void) {\n    i2c_config_t cfg = {.mode = I2C_MODE_MASTER, .sda_io_num = 21, .scl_io_num = 22, .sda_pullup_en = GPIO_PULLUP_ENABLE, .scl_pullup_en = GPIO_PULLUP_ENABLE};\n    cfg.master.clk_speed = 100000;\n    i2c_param_config(I2C_NUM_0, &cfg);\n    i2c_driver_install(I2C_NUM_0, cfg.mode, 0, 0, 0);\n}\n\nvoid app_main(void) {\n    i2c_init();\n    while (1) { vTaskDelay(pdMS_TO_TICKS(1000)); }\n}\n""",
        "timers": """// ESP32 hardware timer periodic callback\n#include "driver/gptimer.h"\n\nstatic bool on_alarm_cb(gptimer_handle_t timer, const gptimer_alarm_event_data_t *edata, void *user_ctx) {\n    (void)timer; (void)edata; (void)user_ctx;\n    return false;\n}\n\nvoid timer_init(void) {\n    gptimer_handle_t timer = NULL;\n    gptimer_config_t cfg = {.clk_src = GPTIMER_CLK_SRC_DEFAULT, .direction = GPTIMER_COUNT_UP, .resolution_hz = 1000000};\n    gptimer_new_timer(&cfg, &timer);\n    gptimer_event_callbacks_t cbs = {.on_alarm = on_alarm_cb};\n    gptimer_register_event_callbacks(timer, &cbs, NULL);\n    gptimer_enable(timer);\n}\n\nvoid app_main(void) {\n    timer_init();\n    while (1) { vTaskDelay(pdMS_TO_TICKS(1000)); }\n}\n""",
    },
    "PIC16F877A": {
        "uart": """// PIC16F877A EUSART transmit example\n#include <xc.h>\n\nvoid uart_init(void) {\n    TRISC6 = 0; TRISC7 = 1;\n    SPBRG = 25;                              // 9600 at 4MHz (BRGH=1)\n    BRGH = 1; SYNC = 0;\n    SPEN = 1; TXEN = 1; CREN = 1;\n}\n\nvoid uart_putc(char c) {\n    while (!TXIF) { }\n    TXREG = c;\n}\n\nvoid main(void) {\n    uart_init();\n    while (1) { uart_putc('P'); }\n}\n""",
        "adc": """// PIC16F877A ADC on AN0\n#include <xc.h>\n\nvoid adc_init(void) {\n    TRISA0 = 1;\n    ADCON1 = 0x80;                           // Right justified, Fosc/32\n    ADCON0 = 0x41;                           // ADON=1, CH0\n}\n\nunsigned int adc_read(void) {\n    GO_nDONE = 1;\n    while (GO_nDONE) { }\n    return ((unsigned int)ADRESH << 8) | ADRESL;\n}\n\nvoid main(void) {\n    adc_init();\n    while (1) { volatile unsigned int sample = adc_read(); (void)sample; }\n}\n""",
        "pwm": """// PIC16F877A CCP1 PWM\n#include <xc.h>\n\nvoid pwm_init(void) {\n    TRISC2 = 0;                              // CCP1 output\n    PR2 = 0xFF;\n    CCP1CON = 0x0C;                          // PWM mode\n    CCPR1L = 0x7F;                           // 50% duty\n    T2CON = 0x04;                            // Timer2 on\n}\n\nvoid main(void) {\n    pwm_init();\n    while (1) { }\n}\n""",
        "gpio": """// PIC16F877A GPIO blink on RB0\n#include <xc.h>\n\nvoid gpio_init(void) {\n    TRISB0 = 0;\n}\n\nvoid delay(void) {\n    for (volatile unsigned int i = 0; i < 50000; ++i) { }\n}\n\nvoid main(void) {\n    gpio_init();\n    while (1) {\n        RB0 = 1; delay();\n        RB0 = 0; delay();\n    }\n}\n""",
        "spi": """// PIC16F877A MSSP SPI master\n#include <xc.h>\n\nvoid spi_init(void) {\n    TRISC3 = 0; TRISC4 = 1; TRISC5 = 0;\n    SSPSTAT = 0x40;\n    SSPCON = 0x21;                           // SPI master, Fosc/16\n}\n\nunsigned char spi_transfer(unsigned char data) {\n    SSPBUF = data;\n    while (!SSPIF) { }\n    SSPIF = 0;\n    return SSPBUF;\n}\n\nvoid main(void) {\n    spi_init();\n    while (1) { volatile unsigned char x = spi_transfer(0xA5); (void)x; }\n}\n""",
        "i2c": """// PIC16F877A MSSP I2C master\n#include <xc.h>\n\nvoid i2c_init(void) {\n    TRISC3 = 1; TRISC4 = 1;\n    SSPCON = 0x28;                           // I2C master mode\n    SSPCON2 = 0x00;\n    SSPADD = 9;                              // ~100kHz @ 4MHz\n    SSPSTAT = 0x80;\n}\n\nvoid i2c_start(void) {\n    SEN = 1;\n    while (SEN) { }\n}\n\nvoid main(void) {\n    i2c_init();\n    while (1) { i2c_start(); }\n}\n""",
        "timers": """// PIC16F877A Timer1 periodic flag polling\n#include <xc.h>\n\nvoid timer1_init(void) {\n    T1CON = 0x31;                            // Prescale 1:8, internal clock\n    TMR1H = 0x0B;\n    TMR1L = 0xDC;                            // preload for periodic tick\n    TMR1IF = 0;\n}\n\nvoid main(void) {\n    timer1_init();\n    while (1) {\n        if (TMR1IF) {\n            TMR1IF = 0;\n            TMR1H = 0x0B; TMR1L = 0xDC;\n            // timer-driven work\n        }\n    }\n}\n""",
    },
}

PIN_CONFIGURATION: dict[str, dict[str, list[dict[str, str]]]] = {
    "LPC2148": {
        "uart": [
            {"signal": "UART0_TXD", "pin": "P0.0", "mode": "Alt function 01"},
            {"signal": "UART0_RXD", "pin": "P0.1", "mode": "Alt function 01"},
        ],
        "adc": [{"signal": "ADC0.1", "pin": "P0.28", "mode": "Analog input"}],
        "pwm": [{"signal": "PWM1", "pin": "P0.0", "mode": "PWM output"}],
        "gpio": [{"signal": "GPIO_OUT", "pin": "P0.10", "mode": "Digital output"}],
        "spi": [
            {"signal": "SCK0", "pin": "P0.4", "mode": "SPI clock"},
            {"signal": "MISO0", "pin": "P0.5", "mode": "SPI input"},
            {"signal": "MOSI0", "pin": "P0.6", "mode": "SPI output"},
        ],
        "i2c": [
            {"signal": "SCL0", "pin": "P0.2", "mode": "I2C clock"},
            {"signal": "SDA0", "pin": "P0.3", "mode": "I2C data"},
        ],
        "timers": [{"signal": "TIMER0", "pin": "Internal", "mode": "Periodic interrupt source"}],
    },
    "Arduino Uno": {
        "uart": [
            {"signal": "TX", "pin": "D1", "mode": "UART transmit"},
            {"signal": "RX", "pin": "D0", "mode": "UART receive"},
        ],
        "adc": [{"signal": "ADC0", "pin": "A0", "mode": "Analog input"}],
        "pwm": [{"signal": "OC1A", "pin": "D9", "mode": "PWM output"}],
        "gpio": [{"signal": "GPIO_OUT", "pin": "D13", "mode": "Digital output"}],
        "spi": [
            {"signal": "MOSI", "pin": "D11", "mode": "SPI output"},
            {"signal": "MISO", "pin": "D12", "mode": "SPI input"},
            {"signal": "SCK", "pin": "D13", "mode": "SPI clock"},
        ],
        "i2c": [
            {"signal": "SDA", "pin": "A4", "mode": "I2C data"},
            {"signal": "SCL", "pin": "A5", "mode": "I2C clock"},
        ],
        "timers": [{"signal": "TIMER0", "pin": "Internal", "mode": "Periodic scheduler tick"}],
    },
    "ESP32": {
        "uart": [
            {"signal": "UART2_TX", "pin": "GPIO17", "mode": "UART transmit"},
            {"signal": "UART2_RX", "pin": "GPIO16", "mode": "UART receive"},
        ],
        "adc": [{"signal": "ADC1_CH6", "pin": "GPIO34", "mode": "Analog input"}],
        "pwm": [{"signal": "LEDC_CH0", "pin": "GPIO18", "mode": "PWM output"}],
        "gpio": [{"signal": "GPIO_OUT", "pin": "GPIO2", "mode": "Digital output"}],
        "spi": [
            {"signal": "MOSI", "pin": "GPIO23", "mode": "SPI output"},
            {"signal": "MISO", "pin": "GPIO19", "mode": "SPI input"},
            {"signal": "SCLK", "pin": "GPIO18", "mode": "SPI clock"},
        ],
        "i2c": [
            {"signal": "SDA", "pin": "GPIO21", "mode": "I2C data"},
            {"signal": "SCL", "pin": "GPIO22", "mode": "I2C clock"},
        ],
        "timers": [{"signal": "GPTIMER0", "pin": "Internal", "mode": "Periodic callback source"}],
    },
    "PIC16F877A": {
        "uart": [
            {"signal": "TX", "pin": "RC6", "mode": "UART transmit"},
            {"signal": "RX", "pin": "RC7", "mode": "UART receive"},
        ],
        "adc": [{"signal": "AN0", "pin": "RA0", "mode": "Analog input"}],
        "pwm": [{"signal": "CCP1", "pin": "RC2", "mode": "PWM output"}],
        "gpio": [{"signal": "GPIO_OUT", "pin": "RB0", "mode": "Digital output"}],
        "spi": [
            {"signal": "SCK", "pin": "RC3", "mode": "SPI clock"},
            {"signal": "SDI", "pin": "RC4", "mode": "SPI input"},
            {"signal": "SDO", "pin": "RC5", "mode": "SPI output"},
        ],
        "i2c": [
            {"signal": "SCL", "pin": "RC3", "mode": "I2C clock"},
            {"signal": "SDA", "pin": "RC4", "mode": "I2C data"},
        ],
        "timers": [{"signal": "TIMER1", "pin": "Internal", "mode": "Periodic tick source"}],
    },
}
