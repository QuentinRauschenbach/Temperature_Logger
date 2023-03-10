/*
 * This file holds all the required HEX commands for working with the DS18B20 sensor
 */

#define CONVERT_T 0x44 // out source this into helper file
#define READ_ROM 0x33 //
#define IS_DS18B20_SENSOR 0x28// family code
#define SKIP_ROM 0xCC
#define READ_SCRATCHPAD 0xBE //
