class Widget3D extends DataWidget{
    constructor() {
        super();
        this.type = "widget3D";
        this.worldId = undefined; // the id of the world instance linked to this widget
        this.onNewSerieAdded = undefined;
        this.onSerieRemoved = undefined;
    }

    addSerie(serie)
    {
        this.series.push(serie);
              
        if (this.onNewSerieAdded != undefined)
            this.onNewSerieAdded();
    }

    removeSerie(serie)
    {
        let idx = this.series.findIndex((s)=>s.id==serie.id);
        if(idx>=0){
            if (this.onSerieRemoved != undefined)
                this.onSerieRemoved(idx);
            this.series[idx].destroy();
            this.series.splice(idx, 1);
        }
              
        this.update();
    }

    destroy(){
        for(let s of this.series) s.destroy();


        // we remove the world linked to this widget from worlds, so it will be removed by the garbage collector
        if (this.worldId != undefined)
        {

            let i = 0;
            let found = false;
            
            while (i < worlds.length && !found) 
            {
                if (worlds[i].id == this.worldId)
                {
                    worlds.splice(i, 1);
                    found = true;
                }

                i++;
            }
        }
    }    

    update(){  
        for(let s of this.series) s.update();
    }

}
