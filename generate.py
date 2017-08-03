#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# generate.py
#
# Copyright (c) 2017 Anup Jayapal Rao <anup.kadam@gmail.com>
#
import sys

from os import listdir
import os.path

import shutil

import json

from collections import OrderedDict

import copy

import colorama
from colorama import Fore, Back, Style

from markdown2 import Markdown
from jinja2 import Template

extJSON = '.json'
extMD = '.md'

tagData = "data"
tagSections = "sections"
tagArticles = "articles"
tagFooter = "footer"
tagTemplate = "template"

pathTemplatesDir = "templates"
templates = {}

pathStatic = "static"

def getEntry(dictDefault, dictMain, keyName):
	strReturn = None
	
	if keyName in dictMain:
		strReturn = dictMain[keyName]
		
	else:
		if keyName in dictDefault:
			strReturn = dictDefault[keyName]
			
	return strReturn

def getMarkdownFromFile(markdowner, pathDomainDir, pathMd):
	
	fullpathMd = os.path.join(pathDomainDir, pathMd)
	fileMD = open(fullpathMd,'rt')					
	strMd = fileMD.read()
	fileMD.close()
	
	strHtml = markdowner.convert(strMd)
	return strHtml

def getProcessedJsonData(pathDomainDir, nodeConfig):
	fnDataEntry = nodeConfig[tagData]
	#print(fnDataEntry)
	
	pathEntry = nodeConfig["template_entry"]
	relpathEntry = os.path.relpath(pathEntry, pathTemplatesDir)
	templateHTML_nodeEntry = Template(templates[relpathEntry])
	
	absfnDataEntry = os.path.join(pathDomainDir, fnDataEntry)
	fdDataEntry = open(absfnDataEntry,'rt')					
	jd_dataentry_str = fdDataEntry.read()
	fdDataEntry.close()
	
	jd_dataentry = json.loads(jd_dataentry_str, object_pairs_hook=OrderedDict)					
	
	#######################################################################################################
	
	# Simple iterator for processing two level markdown reference in json
	markdowner = Markdown()
	sampleKeys = list(jd_dataentry.keys())
	for jsKey in sampleKeys:
		jsValue = jd_dataentry[jsKey]
		
		if "md_" == jsKey[0:3] :
			#print(jsKey)
			mdContent = getMarkdownFromFile(markdowner, pathDomainDir, jsValue)
			jd_dataentry[jsKey] = mdContent
			
		else:
			subEntry = jsValue
			sampleKeys2 = list(subEntry.keys())
			for jsKey2 in sampleKeys2:
				jsValue2 = subEntry[jsKey2]
				
				if "md_" == jsKey2[0:3] :
					#print(jsKey2)
					mdContent = getMarkdownFromFile(markdowner, pathDomainDir, jsValue2)
					subEntry[jsKey2] = mdContent
	
	#######################################################################################################
	
	htmlOutput_DataEntry_All = ''
	for name, value in jd_dataentry.items():
		htmlOutput_DataEntry = templateHTML_nodeEntry.render(name=name, value=value)
		htmlOutput_DataEntry_All = htmlOutput_DataEntry_All + htmlOutput_DataEntry
		
	return htmlOutput_DataEntry_All
		
def getProcessedArticles(pathDomainDir, nodeConfig):
	htmlOutput_Article_All = ''	
	for ArticleName, ArticleConfig in nodeConfig[tagArticles].items():
		print("ArticleName", ArticleName)
		
		strShowTitle = ArticleConfig["ShowTitle"]
		bShowTitle = False
		if True == strShowTitle:
			bShowTitle = True
		del ArticleConfig["ShowTitle"]
						
		pathTemplate = ArticleConfig["template"]
		relpathTemplate = os.path.relpath(pathTemplate, pathTemplatesDir)
		templateHTML_Article = Template(templates[relpathTemplate])
		
		htmlOutput_ArticleEntry_All = ''
		if tagData in ArticleConfig:
			htmlOutput_ArticleEntry_All = getProcessedJsonData(pathDomainDir, ArticleConfig)
			#print(htmlOutput_ArticleEntry_All)
		
		htmlOutput_Article = templateHTML_Article.render(title=ArticleName, bShowTitle=bShowTitle, dataentry_all=htmlOutput_ArticleEntry_All)
		#print(htmlOutput_Article)
		
		htmlOutput_Article_All = htmlOutput_Article_All + htmlOutput_Article
					
	return htmlOutput_Article_All
					
def processPage(pathDomainDir, pageConfig, pageDefaultSchema, jd_config):
	global templates
	global pathTemplatesDir
	
	global tagSections
	
	strTitle = jd_config["title"]
	strTagline = jd_config["tagline"]
	strBannerLogo = jd_config["bannerlogo"]
	strUrl = jd_config["url"]
	strTollFreeNumber = jd_config["toll_free_number"]
	strCopyright = jd_config["copyright"]
	strWebsitename = jd_config["websitename"]
	
	#print(pageConfig)
	#print(pageDefaultSchema)
	
	pathTemplate = getEntry(pageDefaultSchema, pageConfig, "template")
	if None != pathTemplate:
		#print(pathTemplate)
		
		dictComposite = copy.deepcopy(pageDefaultSchema)
		dictComposite["sections"].update(pageConfig["sections"])
		del dictComposite["template"]
		#print(dictComposite["sections"])
		
		relpathTemplate = os.path.relpath(pathTemplate, pathTemplatesDir)
		templateHTML = Template(templates[relpathTemplate])
		
		########################################################################################################################
		
		strMainBody = ""
		
		for entryName, entryConfig in dictComposite.items():
			print("entryName", entryName)
			
			strShowTitle = entryConfig["ShowTitle"]
			bShowTitle = False
			if True == strShowTitle:
				bShowTitle = True
			del entryConfig["ShowTitle"]
					
			if tagSections == entryName:		
				for SectionName, SectionConfig in entryConfig.items():
					print("SectionName", SectionName)
					
					strShowTitle = SectionConfig["ShowTitle"]
					bShowTitle = False
					if True == strShowTitle:
						bShowTitle = True
					del SectionConfig["ShowTitle"]
			
					pathTemplate = SectionConfig["template"]
					relpathTemplate = os.path.relpath(pathTemplate, pathTemplatesDir)
					templateHTML_Section = Template(templates[relpathTemplate])
					
					htmlOutput_SectionEntry_All = ''
					
					if tagData in SectionConfig:
						htmlOutput_SectionEntry_All = getProcessedJsonData(pathDomainDir, SectionConfig)
					elif tagArticles in SectionConfig:
						htmlOutput_SectionEntry_All = getProcessedArticles(pathDomainDir, SectionConfig)
					
					#print("bShowTitle",bShowTitle)
					htmlOutput_Section = templateHTML_Section.render(title=SectionName, bShowTitle=bShowTitle, dataentry_all=htmlOutput_SectionEntry_All)
					#print(htmlOutput_Section)
					
					strMainBody = strMainBody + htmlOutput_Section
			
			elif tagFooter == entryName:	
				
				bShowTitle_Footer = bShowTitle
				
				htmlOutput_Article_All = ''	
				for ArticleName, ArticleConfig in entryConfig[tagArticles].items():
					#print("ArticleName", ArticleName)
					
					strShowTitle = ArticleConfig["ShowTitle"]
					bShowTitle = False
					if True == strShowTitle:
						bShowTitle = True
					del ArticleConfig["ShowTitle"]
									
					pathTemplate = ArticleConfig["template"]
					relpathTemplate = os.path.relpath(pathTemplate, pathTemplatesDir)
					templateHTML_Article = Template(templates[relpathTemplate])
					
					htmlOutput_ArticleEntry_All = ''
					if tagData in ArticleConfig:
						htmlOutput_ArticleEntry_All = getProcessedJsonData(pathDomainDir, ArticleConfig)
					
					htmlOutput_Article = templateHTML_Article.render(title=ArticleName, bShowTitle=bShowTitle, dataentry_all=htmlOutput_ArticleEntry_All)
					#print(htmlOutput_Article)
					
					#######################################################################################################
					
					htmlOutput_Article_All = htmlOutput_Article_All + htmlOutput_Article
					
				pathTemplate = entryConfig["template"]
				relpathTemplate = os.path.relpath(pathTemplate, pathTemplatesDir)
				templateHTML_Footer = Template(templates[relpathTemplate])
				htmlOutput_Footer = templateHTML_Footer.render(
					title=entryName, 
					bShowTitle_Footer=bShowTitle, 
					TollFreeNumber=strTollFreeNumber, 
					Copyright=strCopyright,
					Websitename=strWebsitename,
					articleContent=htmlOutput_Article_All)
					
				strMainBody = strMainBody + htmlOutput_Footer
			
			else:
				if tagTemplate in entryConfig :
					pathTemplate = entryConfig["template"]
					relpathTemplate = os.path.relpath(pathTemplate, pathTemplatesDir)
					templateHTML_Entry = Template(templates[relpathTemplate])
					
					htmlOutput_Entry = templateHTML_Entry.render(tagline=strTagline, bannerlogo=strBannerLogo, Websitename=strWebsitename, TollFreeNumber=strTollFreeNumber)
					#print(htmlOutput_Entry)
					
					strMainBody = strMainBody + htmlOutput_Entry
				
			#htmlOutput_Entry = templateHTML_Entry.render()
			#print(htmlOutput)
			
		########################################################################################################################
		
		htmlOutput = templateHTML.render(Title=strTitle, MainBody=strMainBody)
		#print(htmlOutput)
			
	print()
	
	return htmlOutput

def processConfig(pathConfig, pathOutputDir):
	global templates
	
	fileJSON = open(pathConfig,'rt')					
	jd_config_str = fileJSON.read()
	fileJSON.close()

	jd_config = json.loads(jd_config_str, object_pairs_hook=OrderedDict)
	#print(jd_config)
	
	jd_pages = jd_config["pages"]
	
	keyDefaultSchema = "#default"
	pageDefaultSchema = jd_pages[keyDefaultSchema]
	del jd_pages[keyDefaultSchema]
	#print(pageDefaultSchema)
	
	print("Processing " + Fore.GREEN + pathConfig)
	pathDomainDir = os.path.dirname(pathConfig)
	
	########################################################################################################################
	
	if os.path.exists(pathOutputDir):
		shutil.rmtree(pathOutputDir)
		
	os.mkdir(pathOutputDir)
	
	########################################################################################################################
		
	for pageName, pageConfig in jd_pages.items():
		print(Fore.GREEN + pageName)
		
		htmlOutput = processPage(pathDomainDir, pageConfig, pageDefaultSchema, jd_config)
		
		fnOutput = os.path.join(pathOutputDir, pageName)
		fdHtml = open(fnOutput,'wt')
		fdHtml.write(htmlOutput)
		fdHtml.close()
		
	pathDstStatic = os.path.join(pathOutputDir, pathStatic)
	
	if os.path.exists(pathDstStatic):
		shutil.rmtree(pathDstStatic)
	
	shutil.copytree(pathStatic, pathDstStatic)
	
def processContent(pathConfig, pathOutputDir):
	if os.path.exists(pathConfig):
		processConfig(pathConfig, pathOutputDir)		
	else :
		print(Fore.RED + Style.NORMAL + "Please check if" + Style.BRIGHT + "static" + Style.NORMAL + " and " + Style.BRIGHT +"templates"+ Style.NORMAL + " folder.")
		sys.exit(1)			
	
def processTemplates():
	global pathTemplatesDir
	global templates
	
	listTemplates = listdir(pathTemplatesDir)
	for fnTemplate in listTemplates:
		
		abspathTemplate = os.path.join(pathTemplatesDir,fnTemplate)
		
		fdTemplate = open(abspathTemplate,'rt') 
		strTemplate = fdTemplate.read()
		fdTemplate.close()
		
		templates[fnTemplate] = strTemplate
		
	#print(templates)
	
if "__main__" == __name__ :
	colorama.init(autoreset=True)
	
	if 2 > len(sys.argv) :
		print(Fore.RED + Style.NORMAL + "Usage syntax : " + Fore.WHITE + Style.BRIGHT + "python3 <path_to>/generate.py <path_to>/config.json <path_to>/output_folder")
		print(Fore.RED + Style.NORMAL + "Above command must be executed in folder containing " + Style.BRIGHT + "static" + Style.NORMAL + " and " + Style.BRIGHT +"templates"+ Style.NORMAL + " folder.")
		sys.exit(1)
		
	processTemplates()
	
	processContent(sys.argv[1], sys.argv[2])
