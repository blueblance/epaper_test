

#ifndef QYEG0579RYS683_H
#define QYEG0579RYS683_H

#include "epdif.h"
#define  QYEG0579RYS683


//Display direction
#define FPCLeft   1			// FPC facing left
#define FPCRight  2			// FPC facing right
#define FPCUp  		3			// FPC facing upwards
#define FPCDown   4  		// FPC facing downwards

//2bit
#define black   0x00	/// 00
#define white   0x01	/// 01
#define yellow  0x02	/// 10
#define red     0x03	/// 11

//Screen display area
#define	 MAX_LINE_BYTES   100 
#define  MAX_COLUMN_BYTES 272
#define  ALLSCREEN_BYTES  MAX_LINE_BYTES*MAX_COLUMN_BYTES

#define   X_Addr_Start_H  0x01 
#define   X_Addr_Start_L  0x90 
#define  Y_Addr_Start_H  0x01   
#define  Y_Addr_Start_L  0x10
#define  HTOTAL_DATA1     0x6F
#define  HTOTAL_DATA2     0x5C

// QYEG0579RYS683 commands
#define PSR         0x00		
#define PWR         0x01
#define POF         0x02
#define PFS         0x03
#define PON         0x04
#define BTST        0x06
#define DSLP        0x07
#define DTM         0x10
#define DRF         0x12
#define PLL         0x30
#define TSE         0x41
#define CDI         0x50		
#define TCON        0x60		
#define TRES        0x61		
#define HTOTAL        0x62		
#define GSST       0x65		
#define CCSET         0xE0		
#define PWS         0xE3
#define MS_CTRL         0xEE		


class Epd : public EpdIf {
public:
    int width;
    int height;

    Epd();
    ~Epd();
    int Init(unsigned char Direction);	 //Electronic paper initialization
    void SendCommand(unsigned char command);
    void SendData(unsigned char data);
    void WaitUntilIdle(void);
    void Reset(void);
    void DisplayFrame_And_Sleep(void);
 
    void Acep_color(unsigned char color);

    void SetFrameScreen_ALL_Horizontal(const unsigned char *YRdatas,unsigned char Direction);	//Horizontal display
    void SetFrameScreen_ALL_Vertical(const unsigned char *YRdatas,unsigned char Direction);		//Vertical display
    void ClearFrameMemory(void);
    
private:
    unsigned int reset_pin;
    unsigned int dc_pin;
    unsigned int cs_pin;
    unsigned int busy_pin;

};

#endif /* QYEG0579RYS683_H */

/* END OF FILE */
