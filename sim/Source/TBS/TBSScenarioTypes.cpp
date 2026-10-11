#include "TBSScenarioTypes.h"

bool FTBSScenario::IsValid(FString& OutError) const
{
    if (SchemaVersion.IsEmpty())
    {
        OutError = TEXT("schemaVersion missing");
        return false;
    }
    if (BBox.Num() != 4)
    {
        OutError = TEXT("terrain.bbox must have 4 values [minLon,minLat,maxLon,maxLat]");
        return false;
    }
    if (Entities.Num() == 0)
    {
        OutError = TEXT("scenario has no entities");
        return false;
    }
    for (const FTBSEntityDef& Entity : Entities)
    {
        if (Entity.Id.IsEmpty())
        {
            OutError = TEXT("entity with empty id");
            return false;
        }
        if (Entity.Lat < -90.0 || Entity.Lat > 90.0 || Entity.Lon < -180.0 || Entity.Lon > 180.0)
        {
            OutError = FString::Printf(TEXT("entity %s position out of WGS84 range"), *Entity.Id);
            return false;
        }
    }
    return true;
}
