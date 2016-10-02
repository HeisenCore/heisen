from heisen.core.log import logger
from heisen.config import settings
from heisen.core.shared_memory.register import Register
from heisen.core.shared_memory.shared_memory import SharedMemory


memory = SharedMemory()
register = Register([memory._new_member])
