#include "TBSSessionClient.h"

#include "HttpModule.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"
#include "Misc/CommandLine.h"

bool FTBSSessionClient::LoadHandoffFromCommandLine(FTBSSessionHandoff& OutHandoff, FString& OutError)
{
    if (!FParse::Value(FCommandLine::Get(), TEXT("TBSSessionTicket="), OutHandoff.Ticket))
    {
        OutError = TEXT("missing -TBSSessionTicket=<jwt>");
        return false;
    }
    if (!FParse::Value(FCommandLine::Get(), TEXT("TBSSessionId="), OutHandoff.SessionId))
    {
        OutError = TEXT("missing -TBSSessionId=<uuid>");
        return false;
    }
    FString ApiBase;
    if (!FParse::Value(FCommandLine::Get(), TEXT("TBSApiBase="), ApiBase))
    {
        OutError = TEXT("missing -TBSApiBase=https://api-host");
        return false;
    }
    OutHandoff.ScenarioExportUrl = ApiBase / FString::Printf(TEXT("api/scenarios/export-placeholder"));
    // The real export URL is returned by the ticket endpoint; until the server
    // fetches /api/sessions/{id}/ticket/ itself, compose it from SessionId:
    OutHandoff.ScenarioExportUrl = ApiBase / TEXT("api/sessions") / OutHandoff.SessionId / TEXT("ticket/");
    return true;
}

void FTBSSessionClient::FetchScenario(const FTBSSessionHandoff& Handoff, FTBSScenarioLoaded OnLoaded)
{
    // Step 1: exchange the ticket for scenario export URL + access token.
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request =
        FHttpModule::Get().CreateRequest();
    Request->SetURL(Handoff.ScenarioExportUrl);
    Request->SetVerb(TEXT("POST"));
    Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
    Request->SetHeader(TEXT("Authorization"), FString::Printf(TEXT("Bearer %s"), *Handoff.Ticket));

    Request->OnProcessRequestComplete().BindLambda(
        [Handoff, OnLoaded](FHttpRequestPtr Req, FHttpResponsePtr Resp, bool bConnected)
        {
            if (!bConnected || !Resp.IsValid() || EHttpResponseCodes::IsError(Resp->GetResponseCode()))
            {
                UE_LOG(LogTemp, Error, TEXT("[TBS] ticket exchange failed (connected=%d status=%d)"),
                       bConnected ? 1 : 0, Resp.IsValid() ? Resp->GetResponseCode() : 0);
                FTBSScenario Dummy;
                OnLoaded.ExecuteIfBound(false, Dummy);
                return;
            }

            // Step 2: fetch the scenario export itself.
            TSharedRef<IHttpRequest, ESPMode::ThreadSafe> ScenarioReq =
                FHttpModule::Get().CreateRequest();
            // NOTE: the export URL from the ticket response would be parsed
            // here; kept simple for the scaffold.
            ScenarioReq->SetURL(Handoff.ScenarioExportUrl.Replace(TEXT("/ticket/"), TEXT("/export/")));
            ScenarioReq->SetVerb(TEXT("GET"));
            ScenarioReq->SetHeader(TEXT("Authorization"), FString::Printf(TEXT("Bearer %s"), *Handoff.Ticket));

            ScenarioReq->OnProcessRequestComplete().BindLambda(
                [OnLoaded](FHttpRequestPtr Req2, FHttpResponsePtr Resp2, bool bConnected2)
                {
                    FTBSScenario Scenario;
                    FString Error;
                    if (!bConnected2 || !Resp2.IsValid())
                    {
                        OnLoaded.ExecuteIfBound(false, Scenario);
                        return;
                    }
                    if (!FTBSScenarioParser::Parse(Resp2->GetContentAsString(), Scenario, Error))
                    {
                        UE_LOG(LogTemp, Error, TEXT("[TBS] scenario parse failed: %s"), *Error);
                        OnLoaded.ExecuteIfBound(false, Scenario);
                        return;
                    }
                    OnLoaded.ExecuteIfBound(true, Scenario);
                });
            ScenarioReq->ProcessRequest();
        });
    Request->ProcessRequest();
}

void FTBSSessionClient::IngestAarEvents(const FTBSSessionHandoff& Handoff, const FString& EventsJsonArray)
{
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = FHttpModule::Get().CreateRequest();
    FString Base;
    FParse::Value(FCommandLine::Get(), TEXT("TBSApiBase="), Base);
    Request->SetURL(Base / TEXT("api/sessions") / Handoff.SessionId / TEXT("aar/ingest/"));
    Request->SetVerb(TEXT("POST"));
    Request->SetHeader(TEXT("Content-Type"), TEXT("application/json"));
    Request->SetHeader(TEXT("Authorization"), FString::Printf(TEXT("Bearer %s"), *Handoff.Ticket));
    Request->SetContentAsString(FString::Printf(TEXT("{\"events\": %s}"), *EventsJsonArray));
    Request->ProcessRequest();
}
