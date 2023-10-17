import torch
import asyncio
from PIL import Image
from io import BytesIO
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline, AutoencoderKL
from diffusers import DPMSolverSinglestepScheduler
from diffusers import DPMSolverMultistepScheduler
from diffusers import PNDMScheduler
import discord
from discord.ext import commands

class StableDiffusion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generator = StableDiffusionPipeline.from_single_file("./model/AnythingV5Ink_v5PrtRE.safetensors", torch_dtype = torch.float16)
        self.generator.safety_checker = None
        self.generator.text_encoder.num_hidden_layers = 11
        #generator.vae = AutoencoderKL.from_single_file("./kl-f8-anime2.ckpt", torch_dtype = torch.float16)
        #self.generator.vae = AutoencoderKL.from_single_file("./vae-ft-mse-840000-ema-pruned.safetensors", torch_dtype = torch.float16)
        #generator.scheduler = DPMSolverSinglestepScheduler(use_karras_sigmas=True)
        #generator.scheduler = DPMSolverMultistepScheduler(use_karras_sigmas=True, algorithm_type="sde-dpmsolver++")
        #generator.scheduler = DPMSolverSDEScheduler(use_karras_sigmas=True)
        self.generator.to("cuda")
	
    @commands.command()
    async def txt2img(self, ctx):
        """Generates an image from a prompt
        """
        positive = discord.Embed(title="Text to Image Generation", description="Enter your prompt", color=0xcceeff)
        await ctx.send(embed=positive)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        positive_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        prompt = "best quality, high quality, "+str(positive_message.content)
        await positive_message.delete()

        negative = discord.Embed(title="Text to Image Generation", description="Enter your negative prompt", color=0xcceeff)
        await ctx.send(embed=negative)

        try:
            negative_message = await self.bot.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            neg_prompt = "worst quality, low quality,"
        else:
            neg_prompt = "worst quality, low quality, "+str(negative_message.content)

        await negative_message.delete()

        print("Generating image:" + prompt)
        generating = discord.Embed(title="Generating your Image...", description="Please stand by", color=0xcceeff)
        await ctx.send(embed=generating)
        output = self.generator(prompt=prompt, negative_prompt=neg_prompt, guidance_scale=9.0, num_inference_steps=50).images[0]

        with BytesIO() as image_binary:
            output.save(image_binary, "png")
            image_binary.seek(0)
            image = discord.File(fp=image_binary, filename="image.png", spoiler=True)

        embed = discord.Embed(title="Here is your image", description="This image could have sensitive content", colour=discord.Colour.gold())
        embed.add_field(name='Prompt', value=prompt, inline=False)
        embed.add_field(name='Negative Prompt', value=neg_prompt, inline=False)
        embed.set_image(url="attachment://image.png")
        
        await ctx.send(embed=embed, file=image)

    @commands.command()
    async def setscheduler(self, ctx):
        embed = discord.Embed(title="Scheduler", description="Enter scheduler you want", color=0xcceeff)
        embed.add_field(name='DPM++ 2M Karras', value="dpm2mkarras", inline=False)
        embed.add_field(name='DPM++ 2M SDE Karras', value="dpm2msdekarras", inline=False)
        embed.add_field(name='DPM++ 2M SDE', value="dpm2msde", inline=False)
        embed.add_field(name='Normal', value="normal", inline=False)
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        scheduler = await self.bot.wait_for('message', check=check, timeout=30.0)

        if scheduler == "dpm2mkarras":
            self.generator.scheduler = DPMSolverMultistepScheduler(use_karras_sigmas=True)
        elif scheduler == "dpm2msdekarras":
            self.generator.scheduler = DPMSolverMultistepScheduler(use_karras_sigmas=True, algorithm_type="sde-dpmsolver++")
        elif scheduler == "dpm2msde":
            self.generator.scheduler = DPMSolverMultistepScheduler(use_karras_sigmas=False, algorithm_type="sde-dpmsolver++")
        elif scheduler == "normal":
            self.generator.scheduler = PNDMScheduler()

    
    @commands.command()
    async def model(self, ctx):
        embed = discord.Embed(title="Change Model", description="Enter model you want", color=0xcceeff)
        embed.add_field(name='AnythingV5', value="anythingv5", inline=False)
        embed.add_field(name='ChilloutMix', value="chilloutmix", inline=False)
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        model = await self.bot.wait_for('message', check=check, timeout=30.0)

        if model == "anythingv5":
            self.generator = StableDiffusionPipeline.from_single_file("./model/AnythingV5Ink_v5PrtRE.safetensors", torch_dtype = torch.float16)
            self.generator.safety_checker = None
            self.generator.text_encoder.num_hidden_layers = 11
            self.generator.vae = AutoencoderKL.from_single_file("./vae/vae-ft-mse-840000-ema-pruned.safetensors", torch_dtype = torch.float16)
        elif model == "chilloutmix":
            self.generator = StableDiffusionPipeline.from_single_file("./model/ChilloutMixInk_v5PrtRE.safetensors", torch_dtype = torch.float16)
            self.generator.safety_checker = None
            self.generator.text_encoder.num_hidden_layers = 11
        elif model == "nai":
            self.generator = StableDiffusionPipeline.from_single_file("./model/animefull-latest.ckpt", torch_dtype = torch.float16)
            self.generator.safety_checker = None
            self.generator.text_encoder.num_hidden_layers = 11
            self.generator.vae = AutoencoderKL.from_single_file("./vae/animevae.pt", torch_dtype = torch.float16)

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
    await bot.add_cog(StableDiffusion(bot)) 

