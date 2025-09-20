

#include <stdlib.h>
#include "epd0579RYS683.h"

Epd::~Epd() {
};

Epd::Epd() {
    reset_pin = RST_PIN;
    dc_pin = DC_PIN;
    cs_pin = CS_PIN;
    busy_pin = BUSY_PIN;
};

int Epd::Init(unsigned char Direction) {
    /* this calls the peripheral hardware interface, see epdif */
    if (IfInit() != 0) {
        return -1;
    }
    unsigned char	PSR_Master,PSR_Slave;

// FPC facing left	
	if(Direction==FPCLeft)
	{
		PSR_Master=0x2B;		//UD=1(G0,G1,,Gn-1); SHL=0(Sn-1,,S1.S0);
		PSR_Slave=0x2F;			//UD=1(G0,G1,,Gn-1); SHL=1(S0.S1..Sn-1);
	}

// FPC facing right	
	if(Direction==FPCRight)
	{
		PSR_Master=0x27;		//UD=0(Gn-1...G0); SHL=1(S0,S1...Sn-1);
		PSR_Slave=0x23;			//UD=0(Gn,Gn-1...G1); SHL=0(Sn-1...S1,S0);
	}	
	
// FPC facing upwards
	if(Direction==FPCUp)
	{
		PSR_Master=0x23;		//UD=0(Gn,Gn-1...G1); SHL=0(Sn-1...S1,S0);
		PSR_Slave=0x27;			//UD=0(Gn-1...G0); SHL=1(S0,S1...Sn-1);
	}

// FPC facing downwards
	if(Direction==FPCDown)
	{
		PSR_Master=0x2F;		//UD=1(G0,G1,,Gn-1); SHL=1(S0.S1..Sn-1);
		PSR_Slave=0x2B;			//UD=1(G0,G1,,Gn-1); SHL=0(Sn-1,,S1.S0);
	}		

    /* EPD hardware init start */
    Reset();

    SendCommand(MS_CTRL);		//MS_CTR: Cascade SPI selection Register
    SendData(0x05);     		//MASTER enable

    SendCommand(PSR);		//PSR: Panel Setting Register
    SendData(PSR_Master); 
    SendData(0x69);        

    SendCommand(MS_CTRL);		//MS_CTR: Cascade SPI selection Register
    SendData(0x06);     		//SLAVE enable

    SendCommand(PSR);		//PSR: Panel Setting Register
    SendData(PSR_Slave); 
    SendData(0x69);          

    SendCommand(MS_CTRL);		//MS_CTR: Cascade SPI selection Register
    SendData(0x04);     		//Both Master and Slave
 
    SendCommand(CCSET);		//CCSET: CCSET for temperature input selection
    SendData(0x71);     		//cascaded mode            

    SendCommand(CDI);		//CDI: VCOM and DATA Interval Setting Register 
    SendData(0x37);                     	//border white	

    SendCommand(TRES);		//TRES: Resolution Setting
    SendData(X_Addr_Start_H);                     		
    SendData(X_Addr_Start_L);  
    SendData(Y_Addr_Start_H);                     		
    SendData(Y_Addr_Start_L);       

    SendCommand(GSST);		//GSST: Gate/Source Start Setting Register
    SendData(0x00);                     		
    SendData(0x00);  
    SendData(0x00);                     
    SendData(0x00);      

    SendCommand(HTOTAL);		//HTOTAL: HTOTAL Setting Register
    SendData(HTOTAL_DATA1);                     		
    SendData(HTOTAL_DATA2);  
    
    SendCommand(0xE9);
    SendData(0x01);                     
 
    /* EPD hardware init end */
    return 0;
}

/**
 *  @brief: basic function for sending commands
 */
void Epd::SendCommand(unsigned char command) {
    DigitalWrite(dc_pin, LOW);
    SpiTransfer(command);
}

/**
 *  @brief: basic function for sending data
 */
void Epd::SendData(unsigned char data) {
    DigitalWrite(dc_pin, HIGH);
    SpiTransfer(data);
}

/**
 *  @brief: Wait until the busy_pin goes LOW
 */
void Epd::WaitUntilIdle(void) {
    while(DigitalRead(busy_pin) == LOW) {      //LOW:busy , HIGH: idle
        DelayMs(100);
    }      
}

/**
 *  @brief: module reset.
 *          often used to awaken the module in deep sleep,
 *          see Epd::Sleep();
 */
void Epd::Reset(void) {
    DigitalWrite(reset_pin, LOW);                //module reset    
    DelayMs(200);
    DigitalWrite(reset_pin, HIGH);
    DelayMs(200);    
    WaitUntilIdle();
}


unsigned char Color_get(unsigned char color)
{
	unsigned datas;
	switch(color)
	{
		case 0x00:
			datas=white;	
      break;		
		case 0x01:
			datas=yellow;
		  break;
		case 0x02:
			datas=red;
		  break;		
		case 0x03:
			datas=black;
		  break;			
    default:
      break;			
	}
	 return datas;
}

/**
 *  @brief: put an image buffer to the frame memory.
 *          this won't update the display.
 *          Horizontal display.
 */
void Epd::SetFrameScreen_ALL_Horizontal(const unsigned char *YRdatas,unsigned char Direction)
 {
  unsigned long i,j; 
  unsigned long Left_CTRL,Right_CTRL; 	
  unsigned char temp;
  unsigned char tempOriginal;     
  unsigned char data_H1,data_H2,data_L1,data_L2;	
	
// FPC facing left	
	if(Direction==FPCLeft)
	{
		Left_CTRL=0x06;		//SLAVE
		Right_CTRL=0x05;	//MASTER
	}

// FPC facing right	
	if(Direction==FPCRight)
	{
		Left_CTRL=0x05;		//MASTER
		Right_CTRL=0x06;	//SLAVE
	}	

//Left
    SendCommand(MS_CTRL);		//MS_CTR: Cascade SPI selection Register
    SendData(Left_CTRL);     		
    SendCommand(DTM);        /* Send black and white data */
        for(i=0;i<MAX_COLUMN_BYTES;i++)   
	{ 
    		for(j=0;j<MAX_LINE_BYTES;j++)
		{	  
			temp=*(YRdatas+i*99*2+j);

			data_H1=Color_get(temp>>6&0x03)<<6;			
			data_H2=Color_get(temp>>4&0x03)<<4;
			data_L1=Color_get(temp>>2&0x03)<<2;
			data_L2=Color_get(temp&0x03);
			
			tempOriginal=data_H1|data_H2|data_L1|data_L2;
      			SendData(tempOriginal);
		}
 	}	

 //Right
    SendCommand(MS_CTRL);		//MS_CTR: Cascade SPI selection Register
    SendData(Right_CTRL);     		
    SendCommand(DTM);        /* Send black and white data */
        for(i=0;i<MAX_COLUMN_BYTES;i++)   
	{ 
    		for(j=0;j<MAX_LINE_BYTES;j++)
		{	  
			temp=*(YRdatas+i*99*2+MAX_LINE_BYTES-2+j);

			data_H1=Color_get(temp>>6&0x03)<<6;			
			data_H2=Color_get(temp>>4&0x03)<<4;
			data_L1=Color_get(temp>>2&0x03)<<2;
			data_L2=Color_get(temp&0x03);
			
			tempOriginal=data_H1|data_H2|data_L1|data_L2;
      			SendData(tempOriginal);
		}
 	}	
}


/**
 *  @brief: put an image buffer to the frame memory.
 *          this won't update the display.
 *          Vertical display.
 */
void Epd::SetFrameScreen_ALL_Vertical(const unsigned char *YRdatas,unsigned char Direction)
 {
  unsigned long i,j; 
  unsigned long Up_CTRL,Down_CTRL; 	
  unsigned char temp;
  unsigned char tempOriginal;     
  unsigned char data_H1,data_H2,data_L1,data_L2;	
	
// FPC facing upwards	
	if(Direction==FPCUp)
	{
		Up_CTRL=0x06;		//SLAVE
		Down_CTRL=0x05;	//MASTER
	}

// FPC facing downwards
	if(Direction==FPCDown)
	{
		Up_CTRL=0x05;		//MASTER
		Down_CTRL=0x06;	//SLAVE
	}	

//Up
    SendCommand(MS_CTRL);		//MS_CTR: Cascade SPI selection Register
    SendData(Up_CTRL);     		
    SendCommand(DTM);        /* Send black and white data */
        for(i=0;i<MAX_COLUMN_BYTES;i++)   
	{ 
    		for(j=0;j<MAX_LINE_BYTES;j++)
		{	  
			temp=*(YRdatas+i+j*MAX_COLUMN_BYTES);

			data_H1=Color_get(temp>>6&0x03)<<6;			
			data_H2=Color_get(temp>>4&0x03)<<4;
			data_L1=Color_get(temp>>2&0x03)<<2;
			data_L2=Color_get(temp&0x03);
			
			tempOriginal=data_H1|data_H2|data_L1|data_L2;
      			SendData(tempOriginal);
		}
 	}	

 //Down
    SendCommand(MS_CTRL);		//MS_CTR: Cascade SPI selection Register
    SendData(Down_CTRL);     		
    SendCommand(DTM);        /* Send black and white data */
        for(i=0;i<MAX_COLUMN_BYTES;i++)   
	{ 
    		for(j=0;j<MAX_LINE_BYTES;j++)
		{	  
			temp=*(YRdatas+i+(j+MAX_LINE_BYTES-2)*MAX_COLUMN_BYTES);

			data_H1=Color_get(temp>>6&0x03)<<6;			
			data_H2=Color_get(temp>>4&0x03)<<4;
			data_L1=Color_get(temp>>2&0x03)<<2;
			data_L2=Color_get(temp&0x03);
			
			tempOriginal=data_H1|data_H2|data_L1|data_L2;
      			SendData(tempOriginal);
		}
 	}	
}


/**
 *  @brief: clear the frame memory with the specified color.
 *          this won't update the display.
 */
void Epd::ClearFrameMemory(void) 
{
  unsigned long i,j;
//MASTER
    SendCommand(MS_CTRL);		//MS_CTR: Cascade SPI selection Register
    SendData(0x05);     		//MASTER enable
    SendCommand(DTM);    /* write RAM for white (0x01) */
	for(i=0;i<MAX_COLUMN_BYTES;i++)
		{         
			for(j=0;j<MAX_LINE_BYTES;j++)
			{
			  SendData(0x55);
			}
		} 

//SLAVE
    SendCommand(MS_CTRL);		//MS_CTR: Cascade SPI selection Register
    SendData(0x06);     		//SLAVE enable
    SendCommand(DTM);    /* write RAM for white (0x01) */
	for(i=0;i<MAX_COLUMN_BYTES;i++)
		{         
			for(j=0;j<MAX_LINE_BYTES;j++)
			{
			  SendData(0x55);
			}
		} 
}

/**
 *  @brief: update Full screen refresh
 *          After this command is transmitted, the chip would enter the 
 *          deep-sleep mode to save power. 
 *          The deep sleep mode would return to standby by hardware reset. 
 *          You can use Epd::Init() to awaken
 */

void Epd::DisplayFrame_And_Sleep(void)
 {
    SendCommand(MS_CTRL);		//MS_CTR: Cascade SPI selection Register
    SendData(0x04);     		//Both Master and Slave

    SendCommand(PON);		//Power ON
    WaitUntilIdle();

    SendCommand(DRF);		//Display Refresh
    SendData(0x00);
    WaitUntilIdle();

    SendCommand(POF);		//Power OFF
    SendData(0x00);
    WaitUntilIdle();

    SendCommand(DSLP);		//Deep Sleep
    SendData(0xA5);
    DelayMs(200);    
}




/* END OF FILE */


