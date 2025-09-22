from dagster import job, op


@op
def extract():
    print("Extracting source data...")


@op
def transform():
    print("Transforming data into staging...")


@op
def qalita_cli_version(context):
    # Uses the QALITA resource to print CLI version
    context.resources.qalita.run(["version"])


@op
def qalita_agent_login(context):
    # Prepares agent context and verifies connectivity
    context.resources.qalita.run(["agent", "login"])


@op
def qalita_source_list(context):
    context.resources.qalita.run(["source", "list"])


@op
def qalita_pack_list(context):
    context.resources.qalita.run(["pack", "list"])


@op(config_schema={"source_id": str, "pack_id": str})
def qalita_agent_run(context):
    source_id = context.op_config.get("source_id", "1")
    pack_id = context.op_config.get("pack_id", "1")
    context.resources.qalita.run(["agent", "run", "-s", str(source_id), "-p", str(pack_id)])


@job
def example_qalita_job():
    e = extract()
    t = transform()
    v = qalita_cli_version()
    login = qalita_agent_login()
    sl = qalita_source_list()
    pl = qalita_pack_list()
    run = qalita_agent_run()

    e >> t >> v >> login
    login >> [sl, pl] >> run


