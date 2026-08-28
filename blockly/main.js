import * as Blockly from 'blockly';

console.log('NEW CONDITIONS VERSION LOADED'); 

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
    }, 
    {
        type: 'serve_customer', 
        message0: 'serve customer', 
        previousStatement: null, 
        nextStatement: null, 
        colour: 45 
    }, 
    {
        type: 'collect_money', 
        message0: 'collect money', 
        previousStatement: null, 
        nextStatement: null, 
        colour: 45 
    }, 
    {
        type: 'repeat_times', 
        message0: 'repeat %1 times %2', 
        args0: [
            {
            type: 'field_number', 
            name: 'TIMES', 
            value: 2, 
            min: 1, 
            max: 10, 
            precision: 1
        
            }, 
            {
            type: 'input_statement', 
            name: "DO"
            }
        ], 
    previousStatement: null, 
    nextStatement: null, 
    colour: 210 
    }, 
    {
        type: 'if_customer_nearby', 
        message0: 'if customer nearby %1', 
        args0: [
            {
                type: 'input_statement', 
                name: 'DO'
            }, 
        ], 
        previousStatement: null, 
        nextStatement: null, 
        colour: 120
    }
]); 

console.log('Condition block:', Blockly.Blocks['if_customer_nearby']); 

// add blocks to workspace 
const toolbox = {
    kind: 'categoryToolbox', 
    contents: [
       {
            kind: 'category', 
            name: 'Movement', 
            colour: '200', 
            contents: [
                
                {kind: 'block', type: 'move_up'}, 
                {kind: 'block', type: 'move_down'}, 
                {kind: 'block', type: 'move_left'}, 
                {kind: 'block', type: 'move_right'}, 
                
            ]
       } , 
       {
            kind: 'category', 
            name: 'Actions', 
            colour: '45', 
            contents: [
                {kind: 'block', type: 'serve_customer'}, 
                {kind: 'block', type: 'collect_money'}

            ]
       }, 
       {
            kind: 'category', 
            name: 'Loops', 
            colour: '210', 
            contents: [
                {kind: 'block', type: 'repeat_times'}
            ]
       }, 
       {
            kind: 'category', 
            name: 'Conditions', 
            colour: '120', 
            contents: [
                {
                    kind: 'block', 
                    type: 'if_customer_nearby'
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
)

workspace.addChangeListener(() => {
    updateCommandOutput(); 
}); 

// make blockly generate a command 
function getCommands(){
    const commands = []
    const topBlocks = workspace.getTopBlocks(true); 
    for (const topBlock of topBlocks){
        commands.push(
            ...commandsFromBlock(topBlock)
        ); 
    }
    console.log('Generated commands:', commands); 
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

// recursive section to read nested blocks inside repeat
function commandsFromBlock(block){
    const commands = []; 
    while(block){
        if (block.type === 'move_up'){
            commands.push('up'); 
        }
        else if (block.type === 'move_down'){
            commands.push('down'); 
        }
        else if (block.type === 'move_left'){
            commands.push('left'); 
        }
        else if (block.type === 'move_right'){
            commands.push('right'); 
        }
        else if (block.type === 'serve_customer'){
            commands.push('serve'); 
        }
        else if (block.type === 'collect_money'){
            commands.push('collect'); 
        }
        else if (block.type === 'repeat_times'){
            const times = 
                Number(block.getFieldValue('TIMES')); 
            const firstChild = 
                block.getInputTargetBlock('DO'); 
            const innerCommands = 
                commandsFromBlock(firstChild); 
            for (let i = 0; i < times; i++){
                commands.push(
                    ...innerCommands 
                ); 
            }
        }
        else if (block.type === 'if_customer_nearby'){
            const firstChild = 
                block.getInputTargetBlock('DO'); 
            const innerCommands = 
                commandsFromBlock(firstChild); 
            commands.push({
                type: 'if_customer_nearby', 
                commands: innerCommands
            }); 
        }
        block = block.getNextBlock(); 

    }
    return commands;

}
// run button handler 
document
    .getElementById('runButton')
    .addEventListener('click', () => {
        const commands = getCommands(); 

        // store timestamp-based run ID
        const program = {
            runId: Date.now(), 
            commands: commands
        }; 
        // use local storage to save commands
        localStorage.setItem(
            'streetVendorProgram', 
            JSON.stringify(program) 
        ); 
        updateCommandOutput(); 
        console.log('Saved Blockly program:', program); 
        
    }); 

// reset button 
document
    .getElementById('resetButton')
    .addEventListener('click', () => {
        const program = {
            runId: Date.now(), 
            commands: ['reset']
        }; 
        localStorage.setItem(
            'streetVendorProgram', 
            JSON.stringify(program)
        ); 
        console.log('Reset game:', program); 
    }); 