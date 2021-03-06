/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2021 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32wbxx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define SOIL_M_1_Pin GPIO_PIN_0
#define SOIL_M_1_GPIO_Port GPIOA
#define SOIL_M_2_Pin GPIO_PIN_1
#define SOIL_M_2_GPIO_Port GPIOA
#define SOIL_M_3_Pin GPIO_PIN_2
#define SOIL_M_3_GPIO_Port GPIOA
#define SOIL_M_4_Pin GPIO_PIN_3
#define SOIL_M_4_GPIO_Port GPIOA
#define LD1_Pin GPIO_PIN_4
#define LD1_GPIO_Port GPIOA
#define GREEN_LED_Pin GPIO_PIN_5
#define GREEN_LED_GPIO_Port GPIOA
#define SOIL_T_3_Pin GPIO_PIN_6
#define SOIL_T_3_GPIO_Port GPIOA
#define SOIL_T_4_Pin GPIO_PIN_7
#define SOIL_T_4_GPIO_Port GPIOA
#define SOIL_T_1_Pin GPIO_PIN_8
#define SOIL_T_1_GPIO_Port GPIOA
#define RED_LED_Pin GPIO_PIN_9
#define RED_LED_GPIO_Port GPIOA
#define SOIL_T_5_Pin GPIO_PIN_2
#define SOIL_T_5_GPIO_Port GPIOB
#define LD2_Pin GPIO_PIN_0
#define LD2_GPIO_Port GPIOB
#define LD3_Pin GPIO_PIN_1
#define LD3_GPIO_Port GPIOB
#define B1_Pin GPIO_PIN_10
#define B1_GPIO_Port GPIOA
#define JTMS_Pin GPIO_PIN_13
#define JTMS_GPIO_Port GPIOA
#define JTCK_Pin GPIO_PIN_14
#define JTCK_GPIO_Port GPIOA
#define JTDO_Pin GPIO_PIN_3
#define JTDO_GPIO_Port GPIOB
#define SOIL_T_2_Pin GPIO_PIN_6
#define SOIL_T_2_GPIO_Port GPIOB
/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
