################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (9-2020-q2-update)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
S_SRCS += \
../Core/Startup/startup_stm32wb55cgux.s 

S_DEPS += \
./Core/Startup/startup_stm32wb55cgux.d 

OBJS += \
./Core/Startup/startup_stm32wb55cgux.o 


# Each subdirectory must supply rules for building sources it contributes
Core/Startup/startup_stm32wb55cgux.o: ../Core/Startup/startup_stm32wb55cgux.s Core/Startup/subdir.mk
	arm-none-eabi-gcc -mcpu=cortex-m4 -g3 -c -x assembler-with-cpp -MMD -MP -MF"Core/Startup/startup_stm32wb55cgux.d" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@" "$<"

