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
        type: 'restock_snack', 
        message0: 'restock %1' ,
        args0: [{
            type: 'field_dropdown', 
            name: 'SNACK', 
            options: [
                ['paleta', 'paleta'], 
                ['esquite', 'esquite'], 
                ['raspado', 'raspado']
            ]
        }], 
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
            max: 100, 
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
    }, 
    {
        type: 'choose_paleta_flavor', 
        message0: 'choose paleta flavor %1', 
        args0: [
            {
                type: 'field_dropdown', 
                name: 'FLAVOR', 
                options: [
                    ['fresa', 'fresa'], 
                    ['limon', 'limon'], 
                    ['mango', 'mango'], 
                    ['tamarindo', 'tamarindo']
                ]
            }
        ], 
        previousStatement: null, 
        nextStatement: null, 
        colour: 20
    }, 
    {
        type: 'choose_raspado_flavor', 
        message0: 'choose raspado flavor %1', 
        args0: [
            {
                type: 'field_dropdown', 
                name: 'FLAVOR', 
                options: [
                    ['vainilla', 'vainilla'], 
                    ['fresa', 'fresa'], 
                    ['limon', 'limon'], 
                    ['chicle azul', 'chicle azul']
                ]
            }
        ], 
        previousStatement: null, 
        nextStatement: null, 
        colour: 20
    }, 

    {
        type: 'choose_esquite_ingredient', 
        message0: 'choose esquite ingredient %1', 
        args0: [
            {
                type: 'field_dropdown', 
                name: 'FLAVOR', 
                options: [
                    ['elote', 'elote'], 
                    ['mayonesa', 'mayonesa'], 
                    ['tajin', 'tajin'], 
                    ['limon', 'limon'], 
                    ['queso', 'queso']
                ]
            }
        ], 
        previousStatement: null, 
        nextStatement: null, 
        colour: 20
    }, 

    

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
       {kind: 'block', type: 'restock_snack'}, 
       {
            kind: 'category', 
            name: 'Preparation', 
            colour: '20', 
            contents: [
                {kind: 'block', type: 'choose_paleta_flavor'}, 
                {kind: 'block', type: 'choose_raspado_flavor'}, 
                {kind: 'block', type: 'choose_esquite_ingredient'}
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
       }, 
       
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
        else if (block.type === 'choose_paleta_flavor'){
            const flavor = block.getFieldValue('FLAVOR'); 
            commands.push({
                type: 'choose_paleta_flavor', 
                flavor: flavor 
            }); 
        }

        else if (block.type === 'choose_raspado_flavor'){
            const flavor = block.getFieldValue('FLAVOR'); 
            commands.push({
                type: 'choose_raspado_flavor', 
                flavor: flavor 
            }); 
        }

        else if (block.type === 'choose_esquite_ingredient'){
            const ingredient = block.getFieldValue('FLAVOR'); 
            commands.push({
                type: 'choose_esquite_ingredient', 
                ingredient: ingredient
            }); 
        }

        else if (block.type === 'restock_snack'){
            commands.push({
                type: 'restock_snack', 
                snack: block.getFieldValue('SNACK')
            }); 
        }
        block = block.getNextBlock(); 

    }
    return commands;

}
// tell python whether sutdent used a repeat block 
function workspaceUsesBlockType(type){
    return workspace
    .getAllBlocks(false)
    .some(block => block.type === type); 
}
// run button handler 
document
    .getElementById('runButton')
    .addEventListener('click', () => {
        const commands = getCommands(); 

        // store timestamp-based run ID
        const program = {
            runId: Date.now(), 
            commands: commands, 
            usedRepeat: workspaceUsesBlockType('repeat_times'), 
            usedCondition: workspaceUsesBlockType('if_customer_nearby'), 
            usedServe: workspaceUsesBlockType('serve_customer')
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
            commands: ['reset'], 
            usedRepeat: false, 
            usedCondition: false, 
            usedServe: false
        }; 
        localStorage.setItem(
            'streetVendorProgram', 
            JSON.stringify(program)
        ); 
        console.log('Reset game:', program); 
    }); 