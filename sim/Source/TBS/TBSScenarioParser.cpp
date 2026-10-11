#include "TBSScenarioParser.h"

#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace
{
ETBSSide SideFromString(const FString& S)
{
    if (S == TEXT("red")) return ETBSSide::Red;
    if (S == TEXT("green")) return ETBSSide::Green;
    if (S == TEXT("neutral")) return ETBSSide::Neutral;
    return ETBSSide::Blue;
}

ETBSEntityKind KindFromString(const FString& S)
{
    if (S == TEXT("infantry-soldier")) return ETBSEntityKind::InfantrySoldier;
    if (S == TEXT("team")) return ETBSEntityKind::Team;
    if (S == TEXT("spawn-point")) return ETBSEntityKind::SpawnPoint;
    if (S == TEXT("marker")) return ETBSEntityKind::Marker;
    return ETBSEntityKind::InfantrySquad;
}
} // namespace

bool FTBSScenarioParser::Parse(const FString& JsonBody, FTBSScenario& OutScenario, FString& OutError)
{
    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonBody);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        OutError = TEXT("response is not valid JSON");
        return false;
    }

    OutScenario.SchemaVersion = Root->GetStringField(TEXT("schemaVersion"));

    if (const TSharedPtr<FJsonObject>* Meta)
    {
        if (Root->TryGetObjectField(TEXT("meta"), Meta))
        {
            OutScenario.Name = (*Meta)->GetStringField(TEXT("name"));
        }
    }

    if (const TSharedPtr<FJsonObject>* Terrain)
    {
        if (Root->TryGetObjectField(TEXT("terrain"), Terrain))
        {
            const TArray<TSharedPtr<FJsonValue>>* BBox = nullptr;
            if ((*Terrain)->TryGetArrayField(TEXT("bbox"), BBox) && BBox->Num() == 4)
            {
                for (const TSharedPtr<FJsonValue>& V : *BBox)
                {
                    OutScenario.BBox.Add(V->AsNumber());
                }
            }
            if (const TSharedPtr<FJsonObject>* Source)
            {
                if ((*Terrain)->TryGetObjectField(TEXT("source"), Source))
                {
                    OutScenario.TerrainProvider = (*Source)->GetStringField(TEXT("provider"));
                    int32 AssetId = INDEX_NONE;
                    if ((*Source)->TryGetNumberField(TEXT("assetId"), AssetId))
                    {
                        OutScenario.CesiumAssetId = AssetId;
                    }
                }
            }
        }
    }

    if (const TSharedPtr<FJsonObject>* Env)
    {
        if (Root->TryGetObjectField(TEXT("environment"), Env))
        {
            OutScenario.TimeOfDay = (*Env)->GetStringField(TEXT("timeOfDay"));
            OutScenario.Weather = (*Env)->GetStringField(TEXT("weather"));
            OutScenario.FogDensity = (*Env)->GetNumberField(TEXT("fogDensity"));
        }
    }

    const TArray<TSharedPtr<FJsonValue>>* Entities = nullptr;
    if (Root->TryGetArrayField(TEXT("entities"), Entities))
    {
        for (const TSharedPtr<FJsonValue>& Value : *Entities)
        {
            const TSharedPtr<FJsonObject>* Obj;
            if (!Value->TryGetObject(Obj))
            {
                continue;
            }
            FTBSEntityDef Entity;
            Entity.Id = (*Obj)->GetStringField(TEXT("id"));
            Entity.Kind = KindFromString((*Obj)->GetStringField(TEXT("kind")));
            Entity.Side = SideFromString((*Obj)->GetStringField(TEXT("side")));

            const TSharedPtr<FJsonObject>* Pos;
            if ((*Obj)->TryGetObjectField(TEXT("position"), Pos))
            {
                Entity.Lat = (*Pos)->GetNumberField(TEXT("lat"));
                Entity.Lon = (*Pos)->GetNumberField(TEXT("lon"));
                Entity.AltMeters = (*Pos)->GetNumberField(TEXT("alt"));
            }
            Entity.HeadingDeg = (*Obj)->GetNumberField(TEXT("headingDeg"));

            if (const TSharedPtr<FJsonObject>* Comp)
            {
                if ((*Obj)->TryGetObjectField(TEXT("composition"), Comp))
                {
                    Entity.SoldierCount = (*Comp)->GetNumberField(TEXT("soldiers"));
                    Entity.Loadout = (*Comp)->GetStringField(TEXT("loadout"));
                }
            }

            const TArray<TSharedPtr<FJsonValue>>* Wps = nullptr;
            if ((*Obj)->TryGetArrayField(TEXT("waypoints"), Wps))
            {
                for (const TSharedPtr<FJsonValue>& WpValue : *Wps)
                {
                    const TSharedPtr<FJsonObject>* WpObj;
                    if (!WpValue->TryGetObject(WpObj))
                    {
                        continue;
                    }
                    FTBSWaypoint Wp;
                    Wp.Lat = (*WpObj)->GetNumberField(TEXT("lat"));
                    Wp.Lon = (*WpObj)->GetNumberField(TEXT("lon"));
                    if (double Alt; (*WpObj)->TryGetNumberField(TEXT("alt"), Alt))
                    {
                        Wp.Alt = Alt;
                    }
                    if (double Speed; (*WpObj)->TryGetNumberField(TEXT("speedMs"), Speed))
                    {
                        Wp.SpeedMs = Speed;
                    }
                    Wp.Action = (*WpObj)->GetStringField(TEXT("action"));
                    Entity.Waypoints.Add(Wp);
                }
            }

            OutScenario.Entities.Add(Entity);
        }
    }

    const TArray<TSharedPtr<FJsonValue>>* Objectives = nullptr;
    if (Root->TryGetArrayField(TEXT("objectives"), Objectives))
    {
        for (const TSharedPtr<FJsonValue>& Value : *Objectives)
        {
            const TSharedPtr<FJsonObject>* Obj;
            if (!Value->TryGetObject(Obj))
            {
                continue;
            }
            FTBSObjectiveDef Objective;
            Objective.Id = (*Obj)->GetStringField(TEXT("id"));
            Objective.Description = (*Obj)->GetStringField(TEXT("description"));
            Objective.Points = (*Obj)->GetNumberField(TEXT("points"));
            const TSharedPtr<FJsonObject>* Trigger;
            if ((*Obj)->TryGetObjectField(TEXT("trigger"), Trigger))
            {
                Objective.TriggerType = (*Trigger)->GetStringField(TEXT("type"));
                if (double Radius; (*Trigger)->TryGetNumberField(TEXT("radius"), Radius))
                {
                    Objective.TriggerRadiusMeters = Radius;
                }
            }
            OutScenario.Objectives.Add(Objective);
        }
    }

    return OutScenario.IsValid(OutError);
}
