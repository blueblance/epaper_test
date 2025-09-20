
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "epd0579RYS683.h"
#include "imagedata.h"


// SPI Interactive Functions
void print_help() {
    printf("\n=== 電子紙 SPI 互動命令列 ===\n");
    printf("命令格式:\n");
    printf("  write <cmd> [data1] [data2] ... - 寫入命令和資料\n");
    printf("  read <reg>                      - 讀取暫存器 (如果支援)\n");
    printf("  init <direction>                - 重新初始化 (1=左,2=右,3=上,4=下)\n");
    printf("  clear                           - 清除螢幕\n");
    printf("  display                         - 刷新顯示\n");
    printf("  reset                           - 硬體重置\n");
    printf("  status                          - 檢查BUSY狀態\n");
    printf("  help                            - 顯示此說明\n");
    printf("  exit                            - 離開程式\n");
    printf("\n註: 所有數值請使用十六進位格式 (如: 0x01, 0xFF)\n");
    printf("    常用命令: PSR=0x00, PWR=0x01, PON=0x04, DSLP=0x07, DTM=0x10, DRF=0x12\n\n");
}

void interactive_mode(Epd* epd) {
    char input[256];
    char command[64];
    unsigned int values[16];
    int value_count;

    printf("\n進入 SPI 互動模式...\n");
    print_help();

    while (1) {
        printf("EPD> ");
        fflush(stdout);

        if (!fgets(input, sizeof(input), stdin)) {
            break;
        }

        // 移除換行符號
        input[strcspn(input, "\n")] = 0;

        // 跳過空行
        if (strlen(input) == 0) {
            continue;
        }

        // 解析命令
        value_count = 0;
        char* token = strtok(input, " ");
        if (token) {
            strcpy(command, token);

            // 解析參數
            while ((token = strtok(NULL, " ")) && value_count < 16) {
                values[value_count] = (unsigned int)strtol(token, NULL, 0); // 支援十六進位
                value_count++;
            }
        } else {
            continue;
        }

        // 處理命令
        if (strcmp(command, "exit") == 0 || strcmp(command, "quit") == 0) {
            printf("離開 SPI 互動模式\n");
            break;

        } else if (strcmp(command, "help") == 0) {
            print_help();

        } else if (strcmp(command, "write") == 0) {
            if (value_count < 1) {
                printf("錯誤: write 命令需要至少一個參數 (命令碼)\n");
                continue;
            }

            printf("發送命令: 0x%02X", values[0]);
            epd->SendCommand((unsigned char)values[0]);

            if (value_count > 1) {
                printf(" 資料: ");
                for (int i = 1; i < value_count; i++) {
                    printf("0x%02X ", values[i]);
                    epd->SendData((unsigned char)values[i]);
                }
            }
            printf("\n");

        } else if (strcmp(command, "read") == 0) {
            if (value_count < 1) {
                printf("錯誤: read 命令需要一個參數 (暫存器位址)\n");
                continue;
            }
            printf("註: 此電子紙不支援 SPI 讀取操作\n");

        } else if (strcmp(command, "init") == 0) {
            unsigned char direction = FPCLeft; // 預設
            if (value_count > 0) {
                if (values[0] >= 1 && values[0] <= 4) {
                    direction = (unsigned char)values[0];
                } else {
                    printf("錯誤: 方向必須是 1-4 (1=左,2=右,3=上,4=下)\n");
                    continue;
                }
            }

            printf("重新初始化電子紙 (方向: %d)...\n", direction);
            if (epd->Init(direction) == 0) {
                printf("初始化成功\n");
            } else {
                printf("初始化失敗\n");
            }

        } else if (strcmp(command, "clear") == 0) {
            printf("清除螢幕...\n");
            epd->ClearFrameMemory();

        } else if (strcmp(command, "display") == 0) {
            printf("刷新顯示...\n");
            epd->DisplayFrame_And_Sleep();

        } else if (strcmp(command, "reset") == 0) {
            printf("執行硬體重置...\n");
            epd->Reset();

        } else if (strcmp(command, "status") == 0) {
            printf("等待 BUSY 信號...\n");
            epd->WaitUntilIdle();
            printf("電子紙就緒 (BUSY = HIGH)\n");

        } else {
            printf("未知命令: %s\n", command);
            printf("輸入 'help' 查看可用命令\n");
        }
    }
}

int main(void)
{
    Epd epd;
//Display direction: FPC facing left
    if (epd.Init(FPCLeft) != 0) {
        printf("e-Paper init failed\n");
        return -1;
    }
    /* Display the frame_buffer */
    epd.SetFrameScreen_ALL_Horizontal(gImage_1,FPCLeft);
    epd.DisplayFrame_And_Sleep();
    epd.DelayMs(4000);
  
//Display direction: FPC facing right
    if (epd.Init(FPCRight) != 0) {
        printf("e-Paper init failed\n");
        return -1;
    }
    /* Display the frame_buffer */
    epd.SetFrameScreen_ALL_Horizontal(gImage_2,FPCRight);
    epd.DisplayFrame_And_Sleep();
    epd.DelayMs(4000);

//Display direction: FPC facing downwards
    if (epd.Init(FPCDown) != 0) {
        printf("e-Paper init failed\n");
        return -1;
    }
    /* Display the frame_buffer */
    epd.SetFrameScreen_ALL_Vertical(gImage_3,FPCDown);
    epd.DisplayFrame_And_Sleep();
    epd.DelayMs(4000);

//Display direction: FPC facing upwards
    if (epd.Init(FPCUp) != 0) {
        printf("e-Paper init failed\n");
        return -1;
    }
    /* Display the frame_buffer */
    epd.SetFrameScreen_ALL_Vertical(gImage_3,FPCUp);
    epd.DisplayFrame_And_Sleep();
    epd.DelayMs(4000);

    //all white
    if (epd.Init(FPCLeft) != 0) {
        printf("e-Paper init failed\n");
        return -1;
    }
    epd.ClearFrameMemory();
    epd.DisplayFrame_And_Sleep();
    epd.DelayMs(100);

    printf("\n=== 電子紙示範程式完成 ===\n");
    printf("已展示所有方向的圖像顯示並清除螢幕\n");

    // 進入 SPI 互動模式
    interactive_mode(&epd);

    return 0;
}

