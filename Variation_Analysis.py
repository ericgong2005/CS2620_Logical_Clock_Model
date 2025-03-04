import os
import pandas as pd
import plotly.express as px

def main():
    base_dir = 'Variation_Logs/Trials'

    data = pd.DataFrame(columns=['COMMAND_MAX', 'TIME_MAX','MAX_QUEUE', 'END_LOGICAL_DIFF', 'MAX_LOGICAL_DIFF'])

    for i in range(2, 11, 2):
        for j in range(4, 11, 2):
            folder_name = f"T{i}N{j}"
            folder_path = os.path.join(base_dir, folder_name)
            
            df_list = []
            for num in [2631, 2632, 2633]:
                file_name = f"Log_{num}.txt"
                file_path = os.path.join(folder_path, file_name)
                df_list.append(pd.read_csv(file_path, sep="\t"))
            
            max_queue = max(df_list[0]['QUEUE_SIZE'].max(), df_list[1]['QUEUE_SIZE'].max(), df_list[2]['QUEUE_SIZE'].max())
            end_logical = max(df_list[0]['LOGICAL_TIME'].iloc[-1], df_list[1]['LOGICAL_TIME'].iloc[-1], df_list[2]['LOGICAL_TIME'].iloc[-1])
            max_logical = max((df_list[0]['LOGICAL_TIME'] - df_list[1]['LOGICAL_TIME']).abs().max(),
                              (df_list[1]['LOGICAL_TIME'] - df_list[2]['LOGICAL_TIME']).abs().max(),
                              (df_list[0]['LOGICAL_TIME'] - df_list[2]['LOGICAL_TIME']).abs().max())
            
            data.loc[len(data)] = [j, i, max_queue, end_logical, max_logical]
    
    fig1 = px.scatter_3d(
        data,
        x='COMMAND_MAX',
        y='TIME_MAX',
        z='MAX_QUEUE',
        title='3D Plot of Maximum Queue Length'
    )
    fig1.update_layout(
        scene=dict(
            xaxis_title="Command Max Value",
            yaxis_title="Maximum ticks per second",
            zaxis_title="Maximum Queue Length"
        )
    )
    fig1.write_html("Variation_logs/Plots/Max_queue.html")

    # Plot 2: COMMAND_MAX vs TIME_MAX vs END_LOGICAL_DIFF
    fig2 = px.scatter_3d(
        data,
        x='COMMAND_MAX',
        y='TIME_MAX',
        z='END_LOGICAL_DIFF',
        title='3D Plot of Maximum Logical Clock Difference at the End'
    )
    fig2.update_layout(
        scene=dict(
            xaxis_title="Command Max Value",
            yaxis_title="Maximum ticks per second",
            zaxis_title="Maximum Logical Clock Difference at the End"
        )
    )
    fig2.write_html("Variation_logs/Plots/End_logical_diff.html")

    # Plot 3: COMMAND_MAX vs TIME_MAX vs MAX_LOGICAL_DIFF
    fig3 = px.scatter_3d(
        data,
        x='COMMAND_MAX',
        y='TIME_MAX',
        z='MAX_LOGICAL_DIFF',
        title='3D Plot of Maximum Logical Clock Difference Overall'
    )
    fig3.update_layout(
        scene=dict(
            xaxis_title="Command Max Value",
            yaxis_title="Maximum ticks per second",
            zaxis_title="Maximum Logical Clock Difference Overall"
        )
    )
    fig3.write_html("Variation_logs/Plots/Max_logical_diff.html")




if __name__ == "__main__":
    main()