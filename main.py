##
 #  @filename   :   main.cpp
 #  @brief      :   2.9inch e-paper display (B) demo
 #  @author     :   Yehui from Waveshare
 #
 #  Copyright (C) Waveshare     July 31 2017
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documnetation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to  whom the Software is
 # furished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in
 # all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 ##

import epd2in7b
from PIL import Image, ImageFont,ImageDraw
from apscheduler.schedulers.background import BackgroundScheduler
import coinmarket
import traceback
import time
import RPi.GPIO as GPIO
import pickle
COLORED = 1
UNCOLORED = 0
markets = coinmarket.coinmarkets()
epd = epd2in7b.EPD()
epd.init()
GPIO.setmode(GPIO.BCM)
mode = 0
displayMode = ['Cmc','Bittrex','Quadrigacx']

def stub(self):
    print("stub")

def main():

    updateallcoins()
    scheduler = BackgroundScheduler()
    scheduler.add_job(updateallcoins, 'interval', seconds=45)
    updatedisplayschedule = scheduler.add_job(autoUpdateDisplay, 'interval', seconds=120)
    scheduler.start()
    autoUpdateDisplay()
    chan_list = [5, 6, 13, 19]
    GPIO.setup(chan_list, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(5, GPIO.RISING)
    GPIO.add_event_detect(6, GPIO.RISING)
    GPIO.add_event_detect(13, GPIO.RISING)
    GPIO.add_event_detect(19, GPIO.RISING)
    GPIO.add_event_callback(5, loadHomepage)
    GPIO.add_event_callback(6, nextPage)
    #GPIO.add_event_callback(13, my_callback)
    #GPIO.add_event_callback(19, my_callback)
    while True:
        try:

            # This is here to simulate application activity (which keeps the main thread alive).
            while True:
                time.sleep(.10)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown()

def loadHomepage(self):
    global mode
    mode = 0;
    blackImage, redImage = generateMarketDisplay(markets, 'Cmc')
    epd.init()
    frame_black = epd.get_frame_buffer(blackImage)
    frame_red = epd.get_frame_buffer(redImage)
    epd.display_frame(frame_black, frame_red)

def nextPage(self):
    global mode
    mode += 1
    mode = mode % 3
    print ('nextDisplay ' + str(mode))
    blackImage, redImage = generateMarketDisplay(markets, displayMode[mode])
    epd.init()
    frame_black = epd.get_frame_buffer(blackImage)
    frame_red = epd.get_frame_buffer(redImage)
    epd.display_frame(frame_black, frame_red)
    #pickle.dump(mode, open("mode.pkl", "wb"))
    print("done update display")
def updateallcoins():
    try:
        print("updating coins")
        markets.updatecoin(["BTC"])
        markets.updatecoin(["LTC"])
        markets.updatecoin(["ETH"])
        markets.updatecoin(["ZEC"])

        markets.updatecoin(["BTC","Bittrex"])
        markets.updatecoin(["LTC","Bittrex"])
        markets.updatecoin(["ETH","Bittrex"])
        markets.updatecoin(["ZEC","Bittrex"])

        markets.updatecoin(["BTC","Quadrigacx"])
        markets.updatecoin(["LTC","Quadrigacx"])
        markets.updatecoin(["ETH","Quadrigacx"])
    except Exception as e:
        print(e)
        traceback.print_exc()
        pass

def generateMarketDisplay(markets,exchange):
    startingPositinos = [45,70,95,120,155]
    outputBlack = []
    outputRed = []

    blackImage = Image.new("RGB", (264, 176), (255, 255, 255))
    redImage = Image.new("RGB", (264, 176), (255, 255, 255))
    blackMask = Image.new('1', (264, 176))
    redMask = Image.new('1', (264, 176))
    trans = Image.new('RGBA', (264, 176))
    helveticaFont = ImageFont.truetype('/usr/share/fonts/truetype/freefont/helvetica.ttf', 20)
    helveticaSmall = ImageFont.truetype('/usr/share/fonts/truetype/freefont/helvetica.ttf', 17)
    blackDraw = ImageDraw.Draw(blackMask)
    redDraw = ImageDraw.Draw(redMask)

    for coin in markets.coins:
        coinData = {'name':coin['name']}
        if exchange in coin:
            coinData.update(coin[exchange])
            if coinData['color'] == 'black' :
                outputBlack.append(coinData)
            else:
                outputRed.append(coinData)
    if(exchange == 'Cmc'):
        blackDraw.text((1, 1), "Coin Market Cap" + "\n" + time.strftime("%c"), font=helveticaSmall, fill='#ffffff')
        index = 0
        for c in outputBlack:
            text = c['name'] + ':' + str(c['current']) + " |" + str(c['1h']) + '|' + str(c['24h'])
            blackDraw.text((1, startingPositinos[index]), text, font=helveticaFont, fill='#ffffff')
            index += 1
        total = "Total: " + str(markets.coinmarketcap.stats()['total_market_cap_usd']) + " $ "
        blackDraw.text((1, 155), total, font=helveticaSmall, fill='#ffffff')
        blackImage.paste(trans, (0, 0), blackMask)
        blackImage = blackImage.transpose(Image.ROTATE_90)
        for c in outputRed:
            text = c['name'] + ':' + str(c['current']) + " |" + str(c['1h']) + '|' + str(c['24h'])
            redDraw.text((1, startingPositinos[index]), text, font=helveticaFont, fill='#ffffff')
            index += 1
        redImage.paste(trans, (0, 0), redMask)
        redImage = redImage.transpose(Image.ROTATE_90)
    else:
        blackDraw.text((1, 1), exchange + "\n" + time.strftime("%c"), font=helveticaSmall, fill='#ffffff')
        index = 0
        for c in outputBlack:
            text = c['name'] + ':' + str(c['current']) + " |" + str(c['currentBTC']) + "m" + "| " + "L:" + str(c['low'] + 'm')
            blackDraw.text((1, startingPositinos[index]), text, font=helveticaFont, fill='#ffffff')
            index += 1
        blackImage.paste(trans, (0, 0), blackMask)
        blackImage = blackImage.transpose(Image.ROTATE_90)
        for c in outputRed:
            text = c['name'] + ':' + str(c['current']) + " |" + str(c['currentBTC']) + "m" + "| " + "L:" + str(c['low'] + 'm')
            redDraw.text((1, startingPositinos[index]), text, font=helveticaFont, fill='#ffffff')
            index += 1
        redImage.paste(trans, (0, 0), redMask)
        redImage = redImage.transpose(Image.ROTATE_90)
    return blackImage,redImage

def autoUpdateDisplay():
    print("updaing display")
    epd.init()
    #mode = pickle.load(open("mode.pkl", "rb"))
    blackImage, redImage = generateMarketDisplay(markets, displayMode[mode])
    frame_black = epd.get_frame_buffer(blackImage)
    frame_red = epd.get_frame_buffer(redImage)
    epd.display_frame(frame_black, frame_red)

if __name__ == '__main__':
    main()
