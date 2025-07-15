import uvicorn

if __name__ == "__main__":
    from cje1gw import _run_gateway, _get_port_and_url

    API_PORT = 8888
    FORWARD_ADDR_PORT, FORWARD_ADDR_URL = _get_port_and_url()

    _run_gateway(FORWARD_ADDR_PORT, API_PORT)

    print("SERVING AT:", FORWARD_ADDR_URL)

    print("=========================== NOW YOU CAN ACCESS AT ===========================")
    print(FORWARD_ADDR_PORT)
    print("=============================================================================")

    uvicorn.run("src.main:app", host="0.0.0.0", port=API_PORT, reload=True)
