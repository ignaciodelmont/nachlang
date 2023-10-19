import logging
import warnings

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO, filename="debug.log", filemode="w")
logger = logging.getLogger("nachlang-debug")
