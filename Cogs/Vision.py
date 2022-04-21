import os, asyncio
import json, requests
import discord
from discord.ext import commands

class Vision(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def vision(self, img):
        """
        It classifies whether an image is harmful or not based on the following criteria:
        Adult
        Violence
        Racy

        It need Google Cloud Platform
        """
        my_secret = os.environ['gcloud_key']
        url = "https://vision.googleapis.com/v1/images:annotate"+"?key="+my_secret
        data = {
            "requests": [
            {
                "features": [
                    {
                        "type": "SAFE_SEARCH_DETECTION"
                    }
                ],
                "image": {
                    "source": {
                        "imageUri": img
                    } 
                }
            }
        ]
        }

        js = requests.post(url=url, data=json.dumps(data))
        dic = json.loads(js.text)

        if 'error' in dic['responses'][0]:
            return 1

        return dic['responses'][0]["safeSearchAnnotation"]
	
    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.attachments) > 0:
            for attachment in message.attachments:
                #TODO: GIF 프레임 뜯어내는 코드 작성하기
                if attachment.filename.endswith(".jpg") or attachment.filename.endswith(".jpeg") or attachment.filename.endswith(".png") or attachment.filename.endswith(".webp") or attachment.filename.endswith(".gif"):
                    self.image = attachment.url
                    print("Image Detected")
                    result = self.vision(self.image)

                    while result == 1:
                        await asyncio.sleep(5)
                        result = self.vision(self.image)
                    
                    if (result['adult'] == 'LIKELY') or (result['adult'] == 'VERY_LIKELY') or (result['violence'] == 'LIKELY') or (result['violence'] == 'VERY_LIKELY') or (result['racy'] == 'LIKELY') or (result['racy'] == 'VERY_LIKELY'):
                        embed = discord.Embed(title="Sensitive Content Detected", color=0xcceeff)
                        embed.add_field(name="Adult: ", value=result['adult'], inline=False)
                        embed.add_field(name="Violence: ", value=result['violence'], inline=False)
                        embed.add_field(name="Racy: ", value=result['racy'], inline=False)
                        await message.delete()
                        await message.channel.send(embed=embed)
                        
                    print("Process Complete")
                else:
                    continue
                
        
        elif message.attachments is None:
            return
		

def setup(bot):
    bot.add_cog(Vision(bot))        