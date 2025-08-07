# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "indipyterm",
#     "textual_serve"
# ]
# ///



from textual_serve.server import Server

server = Server("python -m indipyterm")

server.serve()
