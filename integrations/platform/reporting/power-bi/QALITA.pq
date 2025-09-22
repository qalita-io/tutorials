// QALITA Power Query helpers (M)
// - QALITA_SignIn: exchange username/password for JWT
// - QALITA_CreateApiToken: create long-lived API token (requires Bearer)
// - QALITA_GetJson: GET JSON with Bearer header
// - QALITA_TableFromJson: convert list/record JSON to a table
//
// Parameters expected (create in Power BI):
// - QALITA_Url (Text), e.g. https://your-qalita.example.com
// - QALITA_Username (Text)
// - QALITA_Password (Text)
// - QALITA_ApiToken (Text) optional, if you already have a token

let
  QALITA_SignIn = (baseUrl as text, username as text, password as text) as text =>
    let
      url = baseUrl & "/api/v1/auth/signin",
      body = [
        username = username,
        password = password
      ],
      // Use application/x-www-form-urlencoded as FastAPI expects OAuth2PasswordRequestForm
      content = Text.ToBinary(Uri.BuildQueryString(body)),
      response = Web.Contents(
        url,
        [
          Headers = [
            Accept = "application/json",
            #"Content-Type" = "application/x-www-form-urlencoded"
          ],
          Content = content
        ]
      ),
      json = Json.Document(response),
      token = if (json <> null and Record.HasFields(json, "access_token")) then json[access_token] else error "Signin failed: no access_token"
    in
      token,

  QALITA_CreateApiToken = (baseUrl as text, bearerToken as text) as text =>
    let
      url = baseUrl & "/api/v1/tokens/create",
      response = Web.Contents(
        url,
        [
          Headers = [
            Accept = "application/json",
            Authorization = "Bearer " & bearerToken
          ],
          Content = Text.ToBinary("")
        ]
      ),
      json = Json.Document(response),
      token = if (json <> null and Record.HasFields(json, "access_token")) then json[access_token] else error "API token creation failed: no access_token"
    in
      token,

  QALITA_GetJson = (baseUrl as text, pathAndQuery as text, bearerToken as text) as any =>
    let
      // pathAndQuery like "/api/v2/metrics?source_id=1&pack_id=2"
      url = baseUrl & pathAndQuery,
      response = Web.Contents(
        url,
        [
          Headers = [
            Accept = "application/json",
            Authorization = "Bearer " & bearerToken
          ]
        ]
      ),
      json = Json.Document(response)
    in
      json,

  QALITA_TableFromJson = (data as any) as table =>
    let
      normalized = if (Type.Is(Value.Type(data), List.Type)) then data else { data },
      table = Table.FromList(normalized, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
      expanded = Table.ExpandRecordColumn(
        table,
        "Column1",
        Record.FieldNames(if List.Count(normalized) > 0 then normalized{0} else []),
        Record.FieldNames(if List.Count(normalized) > 0 then normalized{0} else [])
      )
    in
      expanded
in
  [
    QALITA_SignIn = QALITA_SignIn,
    QALITA_CreateApiToken = QALITA_CreateApiToken,
    QALITA_GetJson = QALITA_GetJson,
    QALITA_TableFromJson = QALITA_TableFromJson
  ]


