export interface TimingStatsProps {
    value: number;
    className?: string,
}

export function TimingStats({value, className}: TimingStatsProps) {
    const ms = value == -1 ? "-" : Math.round(value * 1000)
    return (
        <div 
            className={className}
        >
            <p>{`${ms} ms`}</p>
        </div>
    )
}