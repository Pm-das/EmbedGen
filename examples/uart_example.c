#include <stdint.h>

// UART init example (generic skeleton)
void uart_init(void) {
    // Configure baud rate registers
    // Configure frame format (8N1)
    // Enable TX/RX
}

void uart_send_byte(uint8_t byte) {
    // Wait until TX FIFO/holding register is ready
    // Send byte
    (void)byte;
}
