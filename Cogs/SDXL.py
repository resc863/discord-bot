import torch
import asyncio
from PIL import Image
from io import BytesIO
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
import discord
from discord import app_commands
from discord.ext import commands

class SDXL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generator = StableDiffusionXLPipeline.from_single_file("./model/animagineXLV31_v31.safetensors", torch_dtype = torch.float16)
        self.generator.safety_checker = None
        self.generator.to("cuda")
        self.generator.enable_model_cpu_offload()
        self.generator.enable_vae_slicing()

    @commands.Cog.listener()
    async def on_ready(self):
        print("SDXL Ready")

    @app_commands.command(name="txt2img", description="Text to Image Generation")
    @app_commands.describe(prompt="prompt", neg_prompt="negative prompt")
    async def txt2img(self, interaction: discord.Interaction, prompt:str, neg_prompt:str):
        """Generates an image from a prompt
        """

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        prompt = "best quality, high quality, very aesthetic, " + prompt

        if neg_prompt == "skip":
            neg_prompt = "worst quality, low quality, very displeasing, photo, 3d"
        else:
            neg_prompt = "worst quality, low quality, very displeasing, photo, 3d" + neg_prompt         

        print("Generating image:" + prompt)
        generating = discord.Embed(title="Generating your Image...", description="Please stand by", color=0xcceeff)
        await interaction.response.send_message(embed=generating)

        output = self.generator(prompt=prompt, negative_prompt=neg_prompt, guidance_scale=7.0, num_inference_steps=28).images[0]

        with BytesIO() as image_binary:
            output.save(image_binary, "png")
            image_binary.seek(0)
            image = discord.File(fp=image_binary, filename="image.png", spoiler=True)

        embed = discord.Embed(title="Here is your image", description="This image could have sensitive content", colour=discord.Colour.gold())
        embed.add_field(name='Prompt', value=prompt, inline=False)
        embed.add_field(name='Negative Prompt', value=neg_prompt, inline=False)
        embed.set_image(url="attachment://image.png")

        await interaction.edit_original_response(embed=embed, attachments=[image])

    @app_commands.command(name="lora_list", description="Show LoRA Adaptor's List")
    async def lora(self, interaction: discord.Interaction):
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        
        embed = discord.Embed(title="LoRA List", description="List of LoRA Adaptor", colour=discord.Colour.gold())
        embed.add_field(name='koreanDollLikeness', value="Korean Idol", inline=False)

        await interaction.edit_original_response(embed=embed)

    @app_commands.command(name="lora", description="Add LoRA Adaptor")
    @app_commands.describe(model="Model")
    async def lora(self, interaction: discord.Interaction, model:str):
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        if model == "koreanDollLikeness":
            self.generator.load_lora_weights("./lora/koreanDollLikeness_v20.safetensors")
        elif model == "unload":
            self.generator.unload_lora_weights()

async def setup(bot):
    await bot.add_cog(SDXL(bot)) 