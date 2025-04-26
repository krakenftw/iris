import asyncio
from tools.linear.service import LinearService
from tools.calenders.googlecal.service import GoogleCalendarService
import dotenv

dotenv.load_dotenv()

from server import start_server

linear_service = LinearService()
calendar_service = GoogleCalendarService()

if __name__ == "__main__":
    asyncio.run(start_server())
