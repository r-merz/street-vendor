import * as Blockly from 'blockly';

// define movement 
Blockly.common.defineBlocksWithJsonArray([
    {
        type: 'move_up', 
        message0: 'move up', 
        previousStatement: null, 
        nextStatement: null, 
        colour: 200
    }, 
    {
        type: 'move_down', 
        message0: 'move down', 
        previousStatement: null, 
        nextStatement: null, 
        colour: 200
    }, 
    {
        type: 'move_left', 
        message0: 'move left', 
        previousStatement: null, 
        nextStatement: null, 
        colour: 200
    }, 
    {
        type: 'move_right', 
        message0: 'move right', 
        previousStatement: null, 
        nextStatement: null, 
        colour: 200
    }
]); 

// add blocks to workspace 
const toolbox = {
    kind: 'categoryToolbox', 
    contents: [
        {
            kind: 'category', 
            name: 'Movement', 
            contents: [
                {
                    kind: 'block', 
                    type: 'move_up'
                }, 
                {
                    kind: 'block', 
                    type: 'move_down'
                }, 
                {
                    kind: 'block', 
                    type: 'move_left'
                }, 
                {
                    kind: 'block', 
                    type: 'move_right'
                }
            ]
        }
    ]
}; 


// make workspace visible 
const workspace = Blockly.inject(
    'blocklyDiv', 
    {
        toolbox: toolbox, 
        trashcan: true 
    }
); 

workspace.addChangeListener(() => {
    updateCommandOutput(); 
}); 

function getCommands(){
    const commands = []; 
    const topBlocks = workspace.getTopBlocks(true); 
    for (const topBlock of topBlocks){
        let block = topBlock; 
        while(block){
            if (block.type == 'move_up'){
                commands.push('up'); 
            }
            else if (block.type == 'move_down'){
                commands.push('down');
            }
            else if (block.type == 'move_left'){
                commands.push('left'); 
            }
            else if (block.type == 'move_right'){
                commands.push('right'); 
            }
            block = block.getNextBlock(); 
        }
    }
    return commands; 
}

// make command list update live when blocks change
function updateCommandOutput(){
    const commands = getCommands(); 
    document
        .getElementById('commandOutput')
        .textContent = 
        `Commands: ${JSON.stringify(commands)}`; 
}

// run button handler 
document
    .getElementById('runButton')
    .addEventListener('click', () => {
        const commands = getCommands(); 
        // use local storage to save commands
        localStorage.setItem(
            'streetVendorCommands', 
            JSON.stringify(commands) 
        ); 
        updateCommandOutput(); 
        console.log('Saved commands:', commands); 
        
    }); 

    
    