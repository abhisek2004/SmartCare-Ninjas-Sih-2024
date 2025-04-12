from bson import ObjectId
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
import smtplib
from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, make_response, session, send_file, after_this_request
import os
import secrets
from pymongo import MongoClient
import jwt
from functools import wraps
from reportlab.lib.pagesizes import A4
import requests
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import qrcode
import io
from log_out import logout_bp
