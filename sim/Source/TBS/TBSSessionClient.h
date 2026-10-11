// Session handoff client: exchanges the signed ticket issued by Django for
// the scenario definition, then reports session state back to the API.
//
// Handoff flow (see docs/architecture.md):
//   1. Instructor launches a session in the web app.
//   2. Backend allocates this dedicated server and mints a short-lived JWT.
//   3. Server starts with -TBSSessionTicket=<jwt> -TBSApiBase=https://...
//   4. This client GETs the scenario export with the ticket and loads it.
#pragma once

#include "CoreMinimal.h"
#include "TBSScenarioTypes.h"

DECLARE_DELEGATE_TwoParams(FTBSScenarioLoaded, bool /*bSuccess*/, const FTBSScenario& /*Scenario*/);

class TBS_API FTBSSessionClient
{
public:
    /** Read -TBSSessionTicket= / -TBSApiBase= from the command line. */
    static bool LoadHandoffFromCommandLine(FTBSSessionHandoff& OutHandoff, FString& OutError);

    /** Fetch the scenario export using the ticket as a bearer token. */
    static void FetchScenario(const FTBSSessionHandoff& Handoff, FTBSScenarioLoaded OnLoaded);

    /** POST /api/sessions/{id}/aar/ingest with a batch of telemetry events. */
    static void IngestAarEvents(const FTBSSessionHandoff& Handoff, const FString& EventsJsonArray);
};
