from __future__ import annotations
            
from datetime import datetime
import pandas as pd  
                    
from demand.environment.schema_adapter import SchemaAdapter
from demand.factors.database import FactorDatabase
from demand.factors.rich_engine import RichFactorEngine
                        
            
class FactorStoreBuilder:
            
    def __init__(self):
         
        self.db = FactorDatabase()
        
        self.db.create()
        
        self.adapter = SchemaAdapter()
        
        self.engine = RichFactorEngine()
        
    def build(self, zip_file):
            
        print()         
            
        print("Reading...")
                
        df = pd.read_csv(

            zip_file,

            sep="\t",
                    
            compression="zip",
                            
            header=None,
                        
            low_memory=False,
                        
            chunksize=50000,
                    
        )
                        
        # Patch 1.2 - Only truncate on first build
        if not hasattr(self, "_started"):
            self.db.truncate()
            self._started = True
        
        # Patch 1.3 - Initialize factor_id as instance variable
        if not hasattr(self, "_factor_id"):
            self._factor_id = 1
                        
        total = 0
                        
        for chunk in df:
                        
            rows = []
                        
            for _, raw in chunk.iterrows():
                      
                event = self.adapter.adapt(raw)
                factors = self.engine.extract(event)

                for factor in factors:

                    date_value = None
                    try:
                        date_value = datetime.strptime(
                            event.date,
                            "%Y%m%d"
                        ).date()
                    except Exception:
                        pass
            
                    rows.append({
         
                        "factor_id": self._factor_id,  # Patch 1.3 - use self._factor_id
        
                        "event_id": event.event_id,
        
                        "observed_at": date_value,
        
                        "factor_type": factor.factor_type,
        
                        "factor_value": str(factor.factor_value),
            
                        "weight": factor.weight,
            
                    })
                    self._factor_id += 1  # Patch 1.3 - use self._factor_id

            if rows:

                self.db.insert_dataframe(
                    pd.DataFrame(rows)
                )
                            
                total += len(rows)  
                print(f"{total:,} factors")
                    
        print()
            
        print("Finished")
         
        print(total)
        
                        
from pathlib import Path
                        
        
if __name__ == "__main__":
        
    builder = FactorStoreBuilder()
            
    history = Path("data_lake/raw/gdelt_history")
            
    files = sorted(history.glob("*.zip"))
    print()

    print(f"Archives: {len(files)}")

    total = len(files)
                    
    for index, file in enumerate(files, start=1):
                            
        print()
                
        print("=" * 80)
        
        print(f"{index}/{total}")
        
        print(file.name)
        
        print("=" * 80)
                        
        builder.build(str(file))
