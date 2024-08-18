import torch
import asyncio
from PIL import Image
from io import BytesIO
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
import discord
from discord.ext import commands

class SDXL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generator = StableDiffusionXLPipeline.from_single_file("./model/animagineXLV31_v31.safetensors", torch_dtype = torch.float16)
        self.generator.safety_checker = None
        self.generator.to("cuda")
        self.generator.enable_model_cpu_offload()
        self.generator.enable_vae_slicing()        

    @commands.command()
    async def txt2img(self, ctx):
        """Generates an image from a prompt
        """
        await ctx.message.delete()

        positive = discord.Embed(title="Text to Image Generation", description="Enter your prompt", color=0xcceeff)
        message = await ctx.send(embed=positive, delete_after=30)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        positive_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        prompt = "best quality, high quality, very aesthetic, "+str(positive_message.content)
        await positive_message.delete()
        await message.delete()

        negative = discord.Embed(title="Text to Image Generation", description="Enter your negative prompt", color=0xcceeff)
        message = await ctx.send(embed=negative, delete_after=30)

        neg_prompt = "worst quality, low quality, very displeasing, "

        try:
            negative_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            neg_prompt = "worst quality, low quality, very displeasing, "
        else:
            if (str(negative_message.content) == "skip") or (str(negative_message.content) == "Skip"):
                neg_prompt = neg_prompt + str(negative_message.content)
                await negative_message.delete()

        await message.delete()            

        print("Generating image:" + prompt)
        generating = discord.Embed(title="Generating your Image...", description="Please stand by", color=0xcceeff)
        message = await ctx.send(embed=generating)
        output = self.generator(prompt=prompt, negative_prompt=neg_prompt, guidance_scale=7.0, num_inference_steps=28).images[0]

        with BytesIO() as image_binary:
            output.save(image_binary, "png")
            image_binary.seek(0)
            image = discord.File(fp=image_binary, filename="image.png", spoiler=True)

        embed = discord.Embed(title="Here is your image", description="This image could have sensitive content", colour=discord.Colour.gold())
        embed.add_field(name='Prompt', value=prompt, inline=False)
        embed.add_field(name='Negative Prompt', value=neg_prompt, inline=False)
        embed.set_image(url="attachment://image.png")

        await message.delete()
        
        await ctx.send(embed=embed, file=image)

    @commands.command()
    async def lora(self, ctx):
        embed = discord.Embed(title="Lora", description="Enter lora you want or type unload to disable lora", color=0xcceeff)
        embed.add_field(name='koreandolllikeness', value="kor", inline=False)
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        model = await self.bot.wait_for('message', check=check, timeout=30.0)

        if model == "kor":
            self.generator.load_lora_weights("./lora/koreanDollLikeness_v20.safetensors")
        elif model == "unload":
            self.generator.unload_lora_weights()

async def setup(bot):
    await bot.add_cog(SDXL(bot)) 