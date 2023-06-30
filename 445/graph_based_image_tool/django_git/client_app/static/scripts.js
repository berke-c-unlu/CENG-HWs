
window.onload = function() {
    handleNodeSelection(0,1,"connect");
    handleNodeSelection(0,2,"connect");
    handleNodeSelection(0,1,"disconnect");
    handleNodeSelection(0,2,"disconnect");
  };


handleNodeSelection = function(nodeid, order, event) {

    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = '/outports';
    const data = {
        'nodeid': nodeid,
    };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(data)
    })
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        if(order==1){
            var selected_node;
            if(event=="connect"){
                selected_node = document.getElementById("outports_connect");
            }
            else if(event=="disconnect"){
                selected_node = document.getElementById("outports_disconnect");
            }
            selected_node.innerHTML="";
            try{
                let count = 0;
                for (var i = 0; i < Object.keys(data.outports).length; i++) {
                    if(data.outports[Object.keys(data.outports)[i]] != null && event=="connect"){
                        continue;
                    }
                    count++;
                    selected_node.innerHTML += "<option value='"+Object.keys(data.outports)[i]+"'>"+Object.keys(data.outports)[i]+"</option>";
                }
                if(count==0 && event=="connect"){
                    selected_node.innerHTML += "<option value='None'>None</option>";
                }
            }
            catch(err){
                selected_node.innerHTML += "<option value='None'>None</option>";
            }
            
        }
        else if(order==2){
            var selected_node;
            if(event=="connect"){
                selected_node = document.getElementById("inports_connect");
            }
            else if(event=="disconnect"){
                selected_node = document.getElementById("inports_disconnect");
            }
            selected_node.innerHTML="";
            try{
                let count = 0;
                for (var i = 0; i < Object.keys(data.inports).length; i++) {
                        if(data.inports[Object.keys(data.inports)[i]] != null && event=="connect"){
                            continue;
                        }
                        count++;
                        selected_node.innerHTML += "<option value='"+Object.keys(data.inports)[i]+"'>"+Object.keys(data.inports)[i]+"</option>";
                    }
                if(count==0 && event=="connect"){
                    selected_node.innerHTML += "<option value='None'>None</option>";
                }
            }
            catch(err){
                selected_node.innerHTML += "<option value='None'>None</option>";
            }
            
        }


    });
};